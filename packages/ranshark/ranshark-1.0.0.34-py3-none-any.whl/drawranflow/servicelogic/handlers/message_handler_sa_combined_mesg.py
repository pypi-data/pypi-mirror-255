import concurrent
import logging
import multiprocessing
import os
import re
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial
from multiprocessing import Manager
from django.utils import timezone

import django

# Set up Django
django.setup()
import numpy as np
import pandas as pd
from drawranflow.models import Identifiers, UploadedFile, Message
from .utils_sa import get_gnb_id, get_trgt_gnb_id, INTERFACE_CONFIG_PD
from django.db import IntegrityError, transaction
import importlib


def split_values(row):
    row = str(row).strip()
    if pd.notna(row) and str(row).lower() != 'nan':
        values = str(row).split(',')
        return values[1] if len(values) > 1 else values[0]
    else:
        return np.nan


# Define reusable functions here
def filter_dataframe_by_protocol(df, protocol):
    return df[df['frame.protocols'].apply(lambda x: protocol.lower() in x.lower() if isinstance(x, str) else False)]


def update_identifiers_df(identifiers_df, condition_df, column_name):
    identifiers_df.at[condition_df.index, column_name] = condition_df.iloc[0][column_name]


BATCH_SIZE = 300


def bulk_update_identifiers(identifiers_df):
    batch_size = BATCH_SIZE
    identifiers_to_create = []

    with transaction.atomic():
        for _, row in identifiers_df.iterrows():
            try:
                c_rnti_value = str(row.get('c_rnti')).strip() if pd.notna(row.get('c_rnti')) and str(
                    row.get('c_rnti')).lower() != 'nan' else '00000'

                identifier_object = Identifiers(
                    c_rnti=c_rnti_value,
                    gnb_du_ue_f1ap_id=row.get('gnb_du_ue_f1ap_id', None),
                    gnb_cu_ue_f1ap_id=row.get('gnb_cu_ue_f1ap_id', None),
                    gnb_cu_cp_ue_e1ap_id=row.get('gnb_cu_cp_ue_e1ap_id', None),
                    gnb_cu_up_ue_e1ap_id=row.get('gnb_cu_up_ue_e1ap_id', None),
                    ran_ue_ngap_id=row.get('ran_ue_ngap_id', None),
                    amf_ue_ngap_id=row.get('amf_ue_ngap_id', None),
                    xnap_src_ran_id=row.get('xnap_src_ran_id', None),
                    xnap_trgt_ran_id=row.get('xnap_trgt_ran_id', None),
                    pci=row.get('pci', None),
                    cucp_f1c_ip=row.get('cucp_f1c_ip', None),
                    du_f1c_ip=row.get('du_f1c_ip', None),
                    gnb_id=row.get('gnb_id', None),
                    uploaded_file_id=row['uploadedFiles_id'],
                    frame_time=row.get('frame_time', None),
                    tmsi=row.get('tmsi', None),
                    plmn=row.get('plmn', None),
                )

                identifiers_to_create.append(identifier_object)

            except IntegrityError as e:
                logging.error(f"IntegrityError occurred during create: {e}")
            except Exception as e:
                logging.error(f"Error occurred during create: {e}")

            # Bulk create in batches
            if len(identifiers_to_create) >= batch_size:
                Identifiers.objects.bulk_create(identifiers_to_create)
                identifiers_to_create = []

        # Final bulk create for any remaining objects
        if identifiers_to_create:
            Identifiers.objects.bulk_create(identifiers_to_create)


def update_identifiers(identifiers_df, match_df, column_name, actualcolumn, identifier_row, index):
    try:
        logging.debug(f"update_identifiers: {identifier_row['c_rnti']} - {column_name} - {actualcolumn}")
        new_value = match_df.iloc[0][actualcolumn]
        identifiers_df.at[index, column_name] = str(new_value)
        logging.debug(f"Updated {column_name} to {new_value}")
        return new_value
    except IndexError:
        logging.warning(f"IndexError during identifier update.")
        return None
    except Exception as e:
        logging.error(f"Error occurred during identifier update: {e}")
        return None


def find_messages(df, condition, additional_condition=None):
    try:
        if additional_condition is None:
            return df[condition]
        else:
            return df[condition & additional_condition]
    except Exception as e:
        logging.error(f"Error occurred during message retrieval: {e}")
        return pd.DataFrame()


def process_identifier_with_crnti(rrc_reestablish_res_df, rrc_setup_df, service_request_df,
                                  ngap_initial_messages_df, df_slice, e1ap_bctxt_mesg_df,
                                  e1ap_bctxt_resp_messages_df, xnap_handover_df, xnap_handover_ack_df,
                                  identifier_row, index):
    def update_identifiers(df_slice, match_df, column_name, actualcolumn, identifier_row, index):
        try:
            logging.debug(f"update_identifiers: {identifier_row['c_rnti']} - {column_name} - {actualcolumn}")
            new_value = match_df.iloc[0][actualcolumn]
            df_slice.at[index, column_name] = str(new_value)
            logging.debug(f"Updated {column_name} to {new_value}")
            return new_value
        except IndexError:
            logging.warning(f"IndexError during identifier update.")
            return None
        except Exception as e:
            logging.error(f"Error occurred during identifier update: {e}")
            return None

    identifier_time = identifier_row['frame_time']
    identifier_du_ip = identifier_row['du_f1c_ip']
    identifier_cucp_ip = identifier_row['cucp_f1c_ip']
    matching_rrc_reestablish_res = find_messages(rrc_reestablish_res_df,
                                                 (rrc_reestablish_res_df[
                                                      'frame.time'] >= identifier_time) &
                                                 (rrc_reestablish_res_df[
                                                      'frame.time'] <= identifier_time
                                                  + pd.Timedelta('1s')) &
                                                 (rrc_reestablish_res_df[
                                                      'ip.src'] == identifier_cucp_ip) &
                                                 (rrc_reestablish_res_df[
                                                      'ip.dst'] == identifier_du_ip) &
                                                 (rrc_reestablish_res_df['f1ap.GNB_DU_UE_F1AP_ID'] ==
                                                  identifier_row['gnb_du_ue_f1ap_id']))
    gnb_cu_ue_f1ap_id = update_identifiers(df_slice, matching_rrc_reestablish_res,
                                           'gnb_cu_ue_f1ap_id', 'f1ap.GNB_CU_UE_F1AP_ID',
                                           identifier_row,
                                           index)

    matching_rrc_setup = find_messages(
        rrc_setup_df,
        (rrc_setup_df['frame.time'] >= identifier_time) &
        (rrc_setup_df['frame.time'] <= identifier_time + pd.Timedelta('1s')) &
        (rrc_setup_df['ip.src'] == identifier_cucp_ip) &
        (rrc_setup_df['ip.dst'] == identifier_du_ip) &
        (rrc_setup_df['f1ap.GNB_DU_UE_F1AP_ID'] == identifier_row['gnb_du_ue_f1ap_id'])
    )

    gnb_cu_ue_f1ap_id = update_identifiers(df_slice, matching_rrc_setup,
                                           'gnb_cu_ue_f1ap_id', 'f1ap.GNB_CU_UE_F1AP_ID',
                                           identifier_row,
                                           index)

    logging.debug(f"gnb_cu_ue_f1ap_id: {gnb_cu_ue_f1ap_id}")

    matching_ngap_setup = find_messages(
        service_request_df,
        (service_request_df['frame.time'] >= identifier_row['frame_time']) &
        (service_request_df['frame.time'] <= identifier_row['frame_time'] + pd.Timedelta('3s')) &
        (service_request_df['ngap.RAN_UE_NGAP_ID'] == gnb_cu_ue_f1ap_id)
    )
    # Update ran_ue_ngap_id in the Identifier DataFrame
    ran_ue_ngap_id = update_identifiers(df_slice, matching_ngap_setup, 'ran_ue_ngap_id',
                                        'ngap.RAN_UE_NGAP_ID', identifier_row, index)

    # Find NGAP Initial Context Setup messages
    matching_ngap_ictxt_setup = find_messages(ngap_initial_messages_df,
                                              (ngap_initial_messages_df['frame.time'] >= identifier_row[
                                                  'frame_time']) &
                                              (ngap_initial_messages_df['frame.time'] <= identifier_row[
                                                  'frame_time'] + pd.Timedelta('2s')) &
                                              (ngap_initial_messages_df[
                                                   'ngap.RAN_UE_NGAP_ID'] == ran_ue_ngap_id))

    # Update amf_ue_ngap_id using the update_identifiers function
    amf_ue_ngap_id = update_identifiers(df_slice, matching_ngap_ictxt_setup, 'amf_ue_ngap_id',
                                        'ngap.AMF_UE_NGAP_ID', identifier_row, index)

    matching_e1ap_setup = find_messages(e1ap_bctxt_mesg_df,
                                        (e1ap_bctxt_mesg_df['frame.time'] >= identifier_row[
                                            'frame_time']) &
                                        (e1ap_bctxt_mesg_df['frame.time'] <= identifier_row[
                                            'frame_time'] + pd.Timedelta('2s')) &
                                        (e1ap_bctxt_mesg_df[
                                             'e1ap.GNB_CU_CP_UE_E1AP_ID'] == gnb_cu_ue_f1ap_id))

    # Update gnb_cu_cp_ue_e1ap_id using the update_identifier_and_log function

    gnb_cu_cp_ue_e1ap_id = update_identifiers(df_slice, matching_e1ap_setup,
                                              'gnb_cu_cp_ue_e1ap_id',
                                              'e1ap.GNB_CU_CP_UE_E1AP_ID', identifier_row, index)

    matching_e1ap_resp_setup = find_messages(e1ap_bctxt_resp_messages_df,
                                             (e1ap_bctxt_resp_messages_df['frame.time'] >=
                                              identifier_row[
                                                  'frame_time']) &
                                             (e1ap_bctxt_resp_messages_df['frame.time'] <=
                                              identifier_row[
                                                  'frame_time'] + pd.Timedelta('10s')) &
                                             (e1ap_bctxt_resp_messages_df[
                                                  'e1ap.GNB_CU_CP_UE_E1AP_ID'] == gnb_cu_cp_ue_e1ap_id))

    # Update gnb_cu_up_ue_e1ap_id using the update_identifier_and_log function
    update_identifiers(df_slice, matching_e1ap_resp_setup, 'gnb_cu_up_ue_e1ap_id',
                       'e1ap.GNB_CU_UP_UE_E1AP_ID', identifier_row, index)

    matching_xnap_req_setup = find_messages(xnap_handover_df,
                                            (xnap_handover_df['frame.time'] >= identifier_row[
                                                'frame_time']) &
                                            (xnap_handover_df['frame.time'] <= identifier_row[
                                                'frame_time'] + pd.Timedelta(minutes=5)) &
                                            (xnap_handover_df[
                                                 'xnap.NG_RANnodeUEXnAPID_src'] == gnb_cu_ue_f1ap_id))

    # Update xnap_src_ran_id using the update_identifier_and_log function
    xnap_src_ran_id = update_identifiers(df_slice, matching_xnap_req_setup, 'xnap_src_ran_id',
                                         'xnap.NG_RANnodeUEXnAPID_src', identifier_row, index)
    matching_xnap_resp_setup = find_messages(xnap_handover_ack_df,
                                             (xnap_handover_ack_df['frame.time'] >= identifier_row[
                                                 'frame_time']) &
                                             (xnap_handover_ack_df[
                                                  'xnap.NG_RANnodeUEXnAPID_src'] == xnap_src_ran_id))

    # Update xnap_trgt_ran_id using the update_identifier_and_log function
    update_identifiers(df_slice, matching_xnap_resp_setup, 'xnap_trgt_ran_id',
                       'xnap.NG_RANnodeUEXnAPID_dst', identifier_row, index)
    return df_slice


def message_handler(df, item_id):
    f1ap_ue_ctxt_req = None
    f1ap_ue_ctxt_res = None
    ngap_path_swith_req = None
    ngap_path_swith_res = None
    try:
        upload_table = UploadedFile.objects.get(id=item_id)
        logging.error(f"Initial analysis started, {upload_table.filename}")

        f1ap_df = filter_dataframe_by_protocol(df, 'f1ap')
        ngap_df = filter_dataframe_by_protocol(df, 'ngap')
        e1ap_df = filter_dataframe_by_protocol(df, 'e1ap')
        xnap_df = filter_dataframe_by_protocol(df, 'xnap')
        f1ap_df.loc[:, 'f1ap.GNB_DU_UE_F1AP_ID'] = f1ap_df['f1ap.GNB_DU_UE_F1AP_ID'].apply(split_values)

        # Find RRC Setup, Reestablishment, and Setup Request messages
        rrc_setup_df = f1ap_df[f1ap_df['_ws.col.info'] == 'RRC Setup']
        rrc_reestablish_res_df = f1ap_df[f1ap_df['_ws.col.info'] == 'RRC Reestablishment']
        rrc_setup_request_df = f1ap_df[
            (f1ap_df['_ws.col.info'] == 'RRC Setup Request') & ~f1ap_df['f1ap.C_RNTI'].isnull()]
        rrc_reestablish_df = f1ap_df[
            (f1ap_df['_ws.col.info'] == 'RRC Reestablishment Request') & ~f1ap_df['f1ap.C_RNTI'].isnull()]

        combined_df = pd.concat([rrc_setup_request_df, rrc_reestablish_df])
        combined_df.loc[:, 'f1ap.nRCellIdentity'] = combined_df['f1ap.nRCellIdentity'].map(get_gnb_id)
        # combined_df.loc[:, 'nr-rrc.ng_5G_S_TMSI_Part1'] = combined_df['nr-rrc.ng_5G_S_TMSI_Part1'].map(get_tmsi)

        service_request_df = ngap_df[
            ((ngap_df['_ws.col.info'] == 'Service request')
             | (ngap_df['_ws.col.info'] == 'Registration request')
             | (ngap_df['_ws.col.info'] == 'Tracking area update request')) & ~ngap_df['ngap.RAN_UE_NGAP_ID'].isnull()
            ]
        ngap_initial_messages_df = ngap_df[
            ((ngap_df['_ws.col.info'] == 'InitialContextSetupRequest') |

             (ngap_df['_ws.col.info'] == 'Registration Reject') |
             (ngap_df['_ws.col.info'].str.contains('Registration reject')) |
             (ngap_df['_ws.col.info'] == 'PDU Session Setup Request')) &
            ~ngap_df['ngap.RAN_UE_NGAP_ID'].isnull() &
            ~ngap_df['ngap.AMF_UE_NGAP_ID'].isnull()
            ]

        e1ap_bctxt_mesg_df = e1ap_df[(e1ap_df['_ws.col.info'] == 'BearerContextSetupRequest')
                                     & ~e1ap_df['e1ap.GNB_CU_CP_UE_E1AP_ID'].isnull()]

        e1ap_bctxt_resp_messages_df = e1ap_df[
            (e1ap_df['_ws.col.info'] == 'BearerContextSetupResponse') |
            (e1ap_df['_ws.col.info'] == 'BearerContextSetupFailure') &
            ~e1ap_df['e1ap.GNB_CU_CP_UE_E1AP_ID'].isnull() &
            ~e1ap_df['e1ap.GNB_CU_UP_UE_E1AP_ID'].isnull()
            ]
        xnap_handover_df = xnap_df[
            (xnap_df['_ws.col.info'] == 'HandoverRequest') &
            ~xnap_df['xnap.NG_RANnodeUEXnAPID_src'].isnull() &
            xnap_df['xnap.NG_RANnodeUEXnAPID_dst'].isnull()
            ]

        xnap_handover_ack_df = xnap_df[
            (xnap_df['_ws.col.info'] == 'HandoverRequestAcknowledge') &
            ~xnap_df['xnap.NG_RANnodeUEXnAPID_src'].isnull() &
            ~xnap_df['xnap.NG_RANnodeUEXnAPID_dst'].isnull()
            ]
        # Define the column mapping
        column_name_mapping = {
            'f1ap.C_RNTI': 'c_rnti',
            'f1ap.GNB_DU_UE_F1AP_ID': 'gnb_du_ue_f1ap_id',
            'f1ap.GNB_CU_UE_F1AP_ID': 'gnb_cu_ue_f1ap_id',
            'nr-rrc.pdcch_DMRS_ScramblingID': 'pci',
            'frame.time': 'frame_time',
            'ngap.RAN_UE_NGAP_ID': 'ran_ue_ngap_id',
            'ngap.AMF_UE_NGAP_ID': 'amf_ue_ngap_id',
            'ip.src': 'du_f1c_ip',
            'ip.dst': 'cucp_f1c_ip',
            'xnap.NG_RANnodeUEXnAPID_src': 'xnap_src_ran_id',
            'xnap.NG_RANnodeUEXnAPID_dst': 'xnap_trgt_ran_id',
            'e1ap.GNB_CU_CP_UE_E1AP_ID': 'gnb_cu_cp_ue_e1ap_id',
            'e1ap.GNB_CU_UP_UE_E1AP_ID': 'gnb_cu_up_ue_e1ap_id',
            'f1ap.nRCellIdentity': 'gnb_id',
            'nr-rrc.ng_5G_S_TMSI_Part1': 'tmsi',
            'f1ap.pLMN_Identity': 'plmn',
        }

        identifiers_df = combined_df[list(column_name_mapping.keys())].copy()
        # Map 'xnap.NR_Cell_Identity' to 'gnb_id' in xnap_df
        xnap_handover_df.loc[:, 'xnap.NR_Cell_Identity'] = xnap_handover_df['xnap.NR_Cell_Identity'].map(
            get_trgt_gnb_id).astype(str)
        # xnap_df['gnb_id'] = xnap_df['xnap.NR_Cell_Identity'].map(get_trgt_gnb_id).to_string()
        # Handle HO calls
        unique_gnb_values = combined_df['f1ap.nRCellIdentity'].unique().tolist()
        unique_gnb_values_str = [str(value) for value in unique_gnb_values]

        logging.debug(f"unique_gnb_values: {unique_gnb_values_str}")
        # Filter xnap_df based on unique_gnb_values
        xnap_df_filtered = xnap_handover_df[xnap_handover_df['xnap.NR_Cell_Identity'].isin(unique_gnb_values_str)]

        logging.debug(f"xnap_df_filtered  {xnap_df_filtered}")
        # Append filtered xnap_df to identifiers_df
        if not xnap_df_filtered.empty:
            temp_df = xnap_df_filtered[[
                'f1ap.C_RNTI',
                'f1ap.GNB_DU_UE_F1AP_ID',
                'f1ap.GNB_CU_UE_F1AP_ID',
                'nr-rrc.pdcch_DMRS_ScramblingID',
                'ip.src',
                'ip.dst',
                'frame.time',
                'ngap.RAN_UE_NGAP_ID',
                'ngap.AMF_UE_NGAP_ID',
                'xnap.NG_RANnodeUEXnAPID_src',
                'xnap.NG_RANnodeUEXnAPID_dst',
                'e1ap.GNB_CU_CP_UE_E1AP_ID',
                'e1ap.GNB_CU_UP_UE_E1AP_ID',
                'f1ap.nRCellIdentity',
                'xnap.NR_Cell_Identity'
            ]]
            identifiers_df = pd.concat([identifiers_df, temp_df], ignore_index=True)

            f1ap_ue_ctxt_req = f1ap_df[f1ap_df['_ws.col.info'] == 'UEContextSetupRequest']
            f1ap_ue_ctxt_res = f1ap_df[f1ap_df['_ws.col.info'] == 'UEContextSetupResponse']
            ngap_path_swith_req = ngap_df[ngap_df['_ws.col.info'] == 'PathSwitchRequest']
            ngap_path_swith_res = ngap_df[ngap_df['_ws.col.info'] == 'PathSwitchRequestAcknowledge']

        # Copy relevant columns from combined_df to identifiers_df
        identifiers_df.rename(columns=column_name_mapping, inplace=True)
        if not xnap_df_filtered.empty:
            # Map 'xnap.NR_Cell_Identity' to 'gnb_id'
            identifiers_df['gnb_id'] = identifiers_df['gnb_id'].combine_first(identifiers_df['xnap.NR_Cell_Identity'])

            identifiers_df.drop(columns=['xnap.NR_Cell_Identity'], inplace=True)
        # Save to Identifiers table
        identifiers_df['uploadedFiles_id'] = item_id

        manager = Manager()
        shared_identifiers_df = manager.list(identifiers_df.to_dict('records'))

        num_processes = min(multiprocessing.cpu_count(), len(shared_identifiers_df))
        chunk_size = max(1, len(identifiers_df) // num_processes)

        with multiprocessing.Pool(num_processes) as pool, multiprocessing.Manager() as manager:
            dataframe_dict = {
                'rrc_reestablish_res_df': rrc_reestablish_res_df,
                'rrc_setup_df': rrc_setup_df,
                'service_request_df': service_request_df,
                'ngap_initial_messages_df': ngap_initial_messages_df,
                'e1ap_bctxt_mesg_df': e1ap_bctxt_mesg_df,
                'e1ap_bctxt_resp_messages_df': e1ap_bctxt_resp_messages_df,
                'xnap_handover_df': xnap_handover_df,
                'xnap_handover_ack_df': xnap_handover_ack_df,
                'f1ap_ue_ctxt_res': f1ap_ue_ctxt_res,
                'f1ap_ue_ctxt_req': f1ap_ue_ctxt_req,
                'ngap_path_swith_req': ngap_path_swith_req,
                'ngap_path_swith_res': ngap_path_swith_res
            }
            results = pool.map(partial(process_slice, dataframes=dataframe_dict),
                               chunks(shared_identifiers_df, chunk_size))

        # Concatenate the processed data from the shared list
        combined_df = pd.concat(results)
        bulk_update_identifiers(combined_df)
        logging.error(f"Initial analysis has been completed!!, {upload_table.filename}")

    except Exception as e:
        logging.error(f"Initial analysis failed, {upload_table.filename}, Error: {e}")
    finally:
        pool.terminate()
        manager.shutdown()


def chunks(iterable, chunk_size):
    """Yield successive chunk_size-sized chunks from iterable."""
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]


def process_slice(slice_data, dataframes=None):
    rrc_reestablish_res_df = dataframes.get('rrc_reestablish_res_df')
    rrc_setup_df = dataframes.get('rrc_setup_df')
    service_request_df = dataframes.get('service_request_df')
    ngap_initial_messages_df = dataframes.get('ngap_initial_messages_df')
    e1ap_bctxt_mesg_df = dataframes.get('e1ap_bctxt_mesg_df')
    e1ap_bctxt_resp_messages_df = dataframes.get('e1ap_bctxt_resp_messages_df')
    xnap_handover_df = dataframes.get('xnap_handover_df')
    xnap_handover_ack_df = dataframes.get('xnap_handover_ack_df')
    f1ap_ue_ctxt_res = dataframes.get('f1ap_ue_ctxt_res')
    f1ap_ue_ctxt_req = dataframes.get('f1ap_ue_ctxt_req')
    ngap_path_swith_req = dataframes.get('ngap_path_swith_req')
    ngap_path_swith_res = dataframes.get('ngap_path_swith_res')

    try:
        if isinstance(slice_data, dict):

            df_slice = pd.DataFrame([slice_data]).astype({
                'c_rnti': str,
                'gnb_du_ue_f1ap_id': str,
                'gnb_cu_ue_f1ap_id': str,
                'pci': str,
                'frame_time': 'datetime64[ns, UTC]',
                'ran_ue_ngap_id': str,
                'amf_ue_ngap_id': str,
                'du_f1c_ip': str,
                'cucp_f1c_ip': str,
                'xnap_src_ran_id': str,
                'xnap_trgt_ran_id': str,
                'gnb_cu_cp_ue_e1ap_id': str,
                'gnb_cu_up_ue_e1ap_id': str,
                'gnb_id': int,
                'tmsi': str,
                'plmn': str,
                'uploadedFiles_id': str
            })
        elif isinstance(slice_data, list):
            # If slice_data is a list of dictionaries, convert it to a DataFrame
            df_slice = pd.DataFrame(slice_data).astype({
                'c_rnti': str,
                'gnb_du_ue_f1ap_id': str,
                'gnb_cu_ue_f1ap_id': str,
                'pci': str,
                'frame_time': 'datetime64[ns, UTC]',
                'ran_ue_ngap_id': str,
                'amf_ue_ngap_id': str,
                'du_f1c_ip': str,
                'cucp_f1c_ip': str,
                'xnap_src_ran_id': str,
                'xnap_trgt_ran_id': str,
                'gnb_cu_cp_ue_e1ap_id': str,
                'gnb_cu_up_ue_e1ap_id': str,
                'gnb_id': int,
                'tmsi': str,
                'plmn': str,
                'uploadedFiles_id': str
            })
        for index, identifier_row in df_slice.iterrows():
            try:
                logging.debug(f"Process ID {os.getpid()}: identifier_row: {identifier_row}")

                identifier_crnti = identifier_row['c_rnti']
                if identifier_crnti == "nan":
                    process_identifier_without_crnti(df_slice, e1ap_bctxt_mesg_df,
                                                     e1ap_bctxt_resp_messages_df, f1ap_ue_ctxt_req, f1ap_ue_ctxt_res,
                                                     xnap_handover_ack_df,
                                                     ngap_path_swith_req, ngap_path_swith_res,
                                                     identifier_row, index)
                if identifier_crnti is not None and not pd.isnull(identifier_crnti) and identifier_crnti != "00000" \
                        or identifier_crnti != 'nan':
                    process_identifier_with_crnti(rrc_reestablish_res_df, rrc_setup_df, service_request_df,
                                                  ngap_initial_messages_df, df_slice, e1ap_bctxt_mesg_df,
                                                  e1ap_bctxt_resp_messages_df, xnap_handover_df,
                                                  xnap_handover_ack_df, identifier_row, index)

            except Exception as e:
                logging.error(f"Process ID {os.getpid()}: Error occurred during row processing: {e}")
    except Exception as e:
        logging.error(f"Process ID {os.getpid()}: Error occurred during row processing: {e}")
    logging.debug(f"Process ID {os.getpid()}: Exiting process_slice")
    return df_slice


def process_identifier_without_crnti(df_slice, e1ap_bctxt_mesg_df, e1ap_bctxt_resp_messages_df, f1ap_ue_ctxt_req,
                                     f1ap_ue_ctxt_res, xnap_handover_ack_df, ngap_path_swith_req, ngap_path_swith_res,
                                     identifier_row,
                                     index):
    def update_identifiers_without(df_slice, match_df, column_name, actualcolumn, identifier_row, index):
        try:
            logging.debug(f"update_identifiers: {identifier_row['c_rnti']} - {column_name} - {actualcolumn}")
            new_value = match_df.iloc[0][actualcolumn]
            df_slice.at[index, column_name] = str(new_value)
            logging.debug(f"Updated {column_name} to {new_value}")
            return new_value
        except IndexError:
            logging.warning(f"IndexError during identifier update.")
            return None
        except Exception as e:
            logging.error(f"Error occurred during identifier update: {e}")
            return None

    xnap_src_ran_id = identifier_row['xnap_src_ran_id']
    # Update gnb_cu_cp_ue_e1ap_id
    matching_e1ap_setup = find_messages(
        e1ap_bctxt_mesg_df,
        (e1ap_bctxt_mesg_df['frame.time'] >= identifier_row['frame_time']) &
        (e1ap_bctxt_mesg_df['frame.time'] <= identifier_row['frame_time'] + pd.Timedelta('1s'))
    )
    gnb_cu_cp_ue_e1ap_id = update_identifiers_without(
        df_slice, matching_e1ap_setup,
        'gnb_cu_cp_ue_e1ap_id', 'e1ap.GNB_CU_CP_UE_E1AP_ID', identifier_row, index
    )
    matching_e1ap_resp_setup = find_messages(
        e1ap_bctxt_resp_messages_df,
        (e1ap_bctxt_resp_messages_df['frame.time'] >= identifier_row['frame_time']) &
        (e1ap_bctxt_resp_messages_df['frame.time'] <= identifier_row['frame_time'] + pd.Timedelta(
            '10s')) &
        (e1ap_bctxt_resp_messages_df['e1ap.GNB_CU_CP_UE_E1AP_ID'] == gnb_cu_cp_ue_e1ap_id)

    )
    gnb_cu_cp_ue_e1ap_id = update_identifiers_without(
        df_slice, matching_e1ap_resp_setup,
        'gnb_cu_up_ue_e1ap_id', 'e1ap.GNB_CU_UP_UE_E1AP_ID', identifier_row, index
    )

    # Update gnb_cu_ue_f1ap_id
    matching_f1ap_req_setup = find_messages(
        f1ap_ue_ctxt_req,
        (f1ap_ue_ctxt_req['frame.time'] >= identifier_row['frame_time']) &
        (f1ap_ue_ctxt_req['frame.time'] <= identifier_row['frame_time'] + pd.Timedelta('1s'))
    )
    gnb_cu_ue_f1ap_id = update_identifiers_without(
        df_slice, matching_f1ap_req_setup,
        'gnb_cu_ue_f1ap_id', 'f1ap.GNB_CU_UE_F1AP_ID', identifier_row, index
    )
    # Update gnb_du_ue_f1ap_id

    matching_f1ap_res = find_messages(
        f1ap_ue_ctxt_res,
        (f1ap_ue_ctxt_res['frame.time'] >= identifier_row['frame_time']) &
        (f1ap_ue_ctxt_res['frame.time'] <= identifier_row['frame_time'] + pd.Timedelta('1s')) &
        (f1ap_ue_ctxt_res['f1ap.GNB_CU_UE_F1AP_ID'] == gnb_cu_ue_f1ap_id)

    )

    gnb_du_ue_f1ap_id = update_identifiers_without(
        df_slice, matching_f1ap_res,
        'gnb_du_ue_f1ap_id', 'f1ap.GNB_DU_UE_F1AP_ID', identifier_row, index
    )
    # Update xnap_trgt_ran_id
    matching_xnap_resp_setup = find_messages(
        xnap_handover_ack_df,
        (xnap_handover_ack_df['frame.time'] >= identifier_row['frame_time']) &
        (xnap_handover_ack_df['xnap.NG_RANnodeUEXnAPID_src'] == xnap_src_ran_id) &
        (xnap_handover_ack_df['xnap.NG_RANnodeUEXnAPID_dst'] == gnb_cu_ue_f1ap_id)

    )
    update_identifiers_without(
        df_slice, matching_xnap_resp_setup,
        'xnap_trgt_ran_id', 'xnap.NG_RANnodeUEXnAPID_dst', identifier_row, index
    )

    # Update ran_ue_ngap_id
    matching_ngap_req = find_messages(
        ngap_path_swith_req,
        (ngap_path_swith_req['frame.time'] >= identifier_row['frame_time']) &
        (ngap_path_swith_req['frame.time'] <= identifier_row['frame_time'] + pd.Timedelta('20s')) &
        (ngap_path_swith_req['ngap.RAN_UE_NGAP_ID'] == gnb_cu_ue_f1ap_id)
    )

    ran_ue_ngap_id = update_identifiers_without(
        df_slice, matching_ngap_req,
        'ran_ue_ngap_id', 'ngap.RAN_UE_NGAP_ID', identifier_row, index
    )

    matching_ngap_res = find_messages(
        ngap_path_swith_res,
        (ngap_path_swith_res['frame.time'] >= identifier_row['frame_time']) &
        (ngap_path_swith_res['frame.time'] <= identifier_row['frame_time'] + pd.Timedelta('20s')) &
        (ngap_path_swith_res['ngap.RAN_UE_NGAP_ID'] == ran_ue_ngap_id)
    )

    update_identifiers_without(
        df_slice, matching_ngap_res,
        'amf_ue_ngap_id', 'ngap.AMF_UE_NGAP_ID', identifier_row, index
    )

    return df_slice


def update_messages_with_identifier_key(df, item_id):
    try:
        upload_table = UploadedFile.objects.get(id=item_id)
        logging.error(f"Started filtering messages for each call flow: {upload_table.filename}")

        # The columns to check for undesired values
        columns_to_check = [
            'f1ap.C_RNTI',
            'f1ap.GNB_DU_UE_F1AP_ID',
            'f1ap.GNB_CU_UE_F1AP_ID',
            'e1ap.GNB_CU_CP_UE_E1AP_ID',
            'e1ap.GNB_CU_UP_UE_E1AP_ID',
            'ngap.RAN_UE_NGAP_ID',
            'ngap.AMF_UE_NGAP_ID',
            'xnap.NG_RANnodeUEXnAPID_src',
            'xnap.NG_RANnodeUEXnAPID_dst',
        ]

        # Specify undesired values
        undesired_values = ["none", "nan", "", None, "NaN", np.nan]

        # Create a mask to filter out rows with undesired values in the specified columns
        mask = df[columns_to_check].apply(
            lambda col: ~col.astype(str).str.lower().isin(undesired_values)
        )

        filtered_df = df[mask.any(axis=1)]
        # identifiers = Identifiers.objects.filter(uploaded_file_id=item_id)
        identifiers = Identifiers.objects.filter(uploaded_file_id=item_id).values()
        identifiers_list = [identifiers] if not isinstance(identifiers, list) else identifiers

        identifiers_list_flat = [item for sublist in identifiers_list for item in sublist]

        messages_to_insert = []
        bulk_update_data = []
        # Prepare shared data
        manager = Manager()
        shared_messages_to_insert = manager.list(messages_to_insert)
        shared_bulk_update_data = manager.list(bulk_update_data)
        num_processes = min(multiprocessing.cpu_count(), len(identifiers))
        chunk_size = max(1, len(identifiers_list_flat) // num_processes)

        # Create a multiprocessing pool
        with multiprocessing.Pool(num_processes) as pool:

            partial_process_slice = partial(process_result,
                                            shared_messages_to_insert=shared_messages_to_insert,
                                            shared_bulk_update_data=shared_bulk_update_data,
                                            filtered_df=filtered_df,
                                            item_id=item_id,
                                            INTERFACE_CONFIG_PD_a=INTERFACE_CONFIG_PD
                                            )

            # Use chunks on the list
            results = pool.map(partial_process_slice,
                               chunks(identifiers_list_flat, chunk_size))
            # pool.starmap(partial_process_slice, chunks_list)

        total_messages = len(shared_messages_to_insert)
        logging.error(f"Messages filter has been completed: {total_messages}")
        logging.error(f"No of Messages to update with stats filter: {total_messages}")

        # Determine the chunk size based on the length of shared_messages_to_insert
        chunk_size = max(1, len(shared_messages_to_insert) // 6)

        # Chunk the shared_messages_to_insert list
        chunksize = [shared_messages_to_insert[i:i + chunk_size] for i in
                     range(0, len(shared_messages_to_insert), chunk_size)]

        # Determine the chunk size based on the length of shared_bulk_update_data
        chunk_size_id = max(1, len(shared_bulk_update_data) // 6)
        logging.error(f"No of Identifiers to update with stats filter: {len(shared_bulk_update_data)}")

        # Chunk the shared_bulk_update_data list
        chunksize_id = [shared_bulk_update_data[i:i + chunk_size_id] for i in
                        range(0, len(shared_bulk_update_data), chunk_size_id)]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                # Submit tasks for each chunk
                futures_create = [executor.submit(bulk_create_messages, chunk) for chunk in chunksize]
                future_update = [executor.submit(bulk_update_identifiers_test, chunk) for chunk in chunksize_id]
                # Wait for both futures to complete
                concurrent.futures.wait([future_update] + [futures_create], timeout=None,
                                        return_when=concurrent.futures.ALL_COMPLETED)
                logging.error("Messages and identifiers update have been completed!")
                setattr(upload_table, 'completeAt', timezone.now())
                setattr(upload_table, 'completed', True)
                upload_table.save()
                logging.error(f"Updated file as completed and set flag to TRUE")

            except TypeError as te:
                if "unhashable type: 'list'" in str(te):
                    # Catch the specific exception and proceed to update upload_table
                    setattr(upload_table, 'completeAt', timezone.now())
                    setattr(upload_table, 'completed', True)
                    upload_table.save()
                    logging.error(f"Updated file as completed and set flag to TRUE")
                pool.terminate()
                manager.shutdown()
            except concurrent.futures.TimeoutError:
                logging.error("Error in processing the completed_futures")

    except TypeError as te:
        if "unhashable type: 'list'" in str(te):
            # Catch the specific exception and proceed to update upload_table
            setattr(upload_table, 'completeAt', timezone.now())
            setattr(upload_table, 'completed', True)
            upload_table.save()
            logging.error(f"Updated file as completed and set flag to TRUE")
        pool.terminate()
        manager.shutdown()
    except Exception as e:
        logging.error(f"Exception during update_messages_with_identifier_key: {e}")
        pass
    finally:
        pool.terminate()
        manager.shutdown()


# Function to be executed by each thread/process
def bulk_create_messages(chunk):
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Use ThreadPoolExecutor to parallelize message instance creation
            message_instances = list(executor.map(create_message_instance, chunk))

        # Bulk create messages
        Message.objects.bulk_create(message_instances)

    except Exception as e:
        logging.error(f"Error in processing bulk_create_messages {e}")


def create_message_instance(row):
    return Message(
        frame_number=row['frame.number'],
        frame_time=row['frame.time'],
        ip_src=row['ip.src'],
        ip_dst=row['ip.dst'],
        protocol=row['frame.protocols'],
        f1_proc=row['f1ap.procedureCode'],
        e1_proc=row['e1ap.procedureCode'],
        ng_proc=row['ngap.procedureCode'],
        c1_rrc=row['f1ap.pLMN_Identity'],
        c2_rrc=row['nr-rrc.ng_5G_S_TMSI_Part1'],
        mm_message_type=row['nas-5gs.mm.message_type'],
        sm_message_type=row['nas-5gs.sm.message_type'],
        message=row['_ws.col.info'],
        src_node=row["srcNode"],
        dst_node=row["dstNode"],
        message_json=None,
        c_rnti=row['f1ap.C_RNTI'],
        gnb_du_ue_f1ap_id=row['f1ap.GNB_DU_UE_F1AP_ID'],
        gnb_cu_ue_f1ap_id=row['f1ap.GNB_CU_UE_F1AP_ID'],
        gnb_cu_cp_ue_e1ap_id=row['e1ap.GNB_CU_CP_UE_E1AP_ID'],
        gnb_cu_up_ue_e1ap_id=row['e1ap.GNB_CU_UP_UE_E1AP_ID'],
        ran_ue_ngap_id=row['ngap.RAN_UE_NGAP_ID'],
        amf_ue_ngap_id=row['ngap.AMF_UE_NGAP_ID'],
        xnap_src_ran_id=row['xnap.NG_RANnodeUEXnAPID_src'],
        xnap_trgt_ran_id=row['xnap.NG_RANnodeUEXnAPID_dst'],
        uploaded_file_id=item_id,
        gnb_id=row['gnb_id'],
        identifiers_id=identifier_data.id,
        f1ap_cause=row['f1ap.cause_desc'],
        ngap_cause=row['ngap.cause_desc'],
        nas_cause=row['nas.cause_desc']
    )

def create_filter_conditions(identifier_data, filtered_df):
    filter_conditions = pd.Series(False, index=filtered_df.index)

    if identifier_data["c_rnti"] != 'nan' and identifier_data["gnb_du_ue_f1ap_id"] != 'nan' and identifier_data[
        "c_rnti"] != '00000':
        filter_conditions |= ((filtered_df['f1ap.C_RNTI'] == identifier_data["c_rnti"]) &
                              (filtered_df['f1ap.GNB_DU_UE_F1AP_ID'] == identifier_data["gnb_du_ue_f1ap_id"]) &
                              (filtered_df['frame.time'] == identifier_data["frame_time"]))
    if identifier_data["gnb_du_ue_f1ap_id"] != 'nan' and identifier_data["gnb_cu_ue_f1ap_id"] != 'nan':
        filter_conditions |= (
                (filtered_df['f1ap.GNB_CU_UE_F1AP_ID'] == identifier_data["gnb_cu_ue_f1ap_id"]) &
                (filtered_df['f1ap.GNB_DU_UE_F1AP_ID'] == identifier_data["gnb_du_ue_f1ap_id"]) &
                (filtered_df['frame.time'] > identifier_data["frame_time"]))

    if identifier_data["gnb_cu_cp_ue_e1ap_id"] != 'nan' and identifier_data["gnb_cu_up_ue_e1ap_id"] != 'nan':
        filter_conditions |= (
                (filtered_df['e1ap.GNB_CU_CP_UE_E1AP_ID'] == identifier_data["gnb_cu_cp_ue_e1ap_id"]) &
                (filtered_df['frame.time'] > identifier_data["frame_time"]) |
                ((filtered_df['e1ap.GNB_CU_CP_UE_E1AP_ID'] == identifier_data["gnb_cu_cp_ue_e1ap_id"]) &
                 (filtered_df['e1ap.GNB_CU_UP_UE_E1AP_ID'] == identifier_data["gnb_cu_up_ue_e1ap_id"]) &
                 (filtered_df['frame.time'] > identifier_data["frame_time"])))

    if identifier_data["ran_ue_ngap_id"] != 'nan' and identifier_data["amf_ue_ngap_id"] != 'nan':
        filter_conditions |= (
                (filtered_df['ngap.RAN_UE_NGAP_ID'] == identifier_data["ran_ue_ngap_id"]) &
                (filtered_df['frame.time'] > identifier_data["frame_time"]) |
                ((filtered_df['ngap.RAN_UE_NGAP_ID'] == identifier_data["ran_ue_ngap_id"]) &
                 (filtered_df['ngap.AMF_UE_NGAP_ID'] == identifier_data["amf_ue_ngap_id"]) &
                 (filtered_df['frame.time'] > identifier_data["frame_time"])))

    if identifier_data["xnap_src_ran_id"] != 'nan':
        filter_conditions |= (
                (filtered_df['xnap.NG_RANnodeUEXnAPID_src'] == identifier_data["xnap_src_ran_id"]) &
                (filtered_df['frame.time'] >= identifier_data["frame_time"]))

    if identifier_data["xnap_trgt_ran_id"] != 'nan':
        filter_conditions |= (
                (filtered_df['xnap.NG_RANnodeUEXnAPID_dst'] == identifier_data["xnap_trgt_ran_id"]) &
                (filtered_df['frame.time'] > identifier_data["frame_time"]))

    if identifier_data["gnb_cu_cp_ue_e1ap_id"] != 'nan' and identifier_data["gnb_cu_up_ue_e1ap_id"] == 'nan':
        filter_conditions |= (
                (filtered_df['e1ap.GNB_CU_CP_UE_E1AP_ID'] == identifier_data["gnb_cu_cp_ue_e1ap_id"]) &
                (filtered_df['e1ap.GNB_CU_UP_UE_E1AP_ID'].isna() &
                 (filtered_df['frame.time'] > identifier_data["frame_time"])))

    if identifier_data["ran_ue_ngap_id"] != 'nan' and identifier_data["amf_ue_ngap_id"] == 'nan':
        filter_conditions |= (
                (filtered_df['ngap.RAN_UE_NGAP_ID'] == identifier_data["ran_ue_ngap_id"]) &
                filtered_df['ngap.AMF_UE_NGAP_ID'].isna() &
                (filtered_df['frame.time'] > identifier_data["frame_time"]))

    updated_messages = filtered_df[filter_conditions]
    condition = ((updated_messages['_ws.col.info'] == 'UEContextReleaseComplete') &
                 updated_messages['frame.protocols'].str.contains('ngap'))
    condition2 = ((updated_messages['_ws.col.info'] == 'BearerContextReleaseComplete') &
                  updated_messages['frame.protocols'].str.contains('e1ap'))
    if condition2.any() or condition.any():  # If the condition is met at least once
        if condition2.any():
            first_occurrence = condition2.idxmax()
            # Check UEContextReleaseComplete in the next couple of rows
            next_rows = updated_messages.loc[first_occurrence + 1:first_occurrence + 2, '_ws.col.info']
            check_uecontext = (next_rows == 'UEContextReleaseComplete').any()
            if check_uecontext:
                updated_messages = updated_messages.loc[:first_occurrence + 2].copy()
            else:
                updated_messages = updated_messages.loc[:first_occurrence].copy()
        else:
            first_occurrence = condition.idxmax()
            updated_messages = updated_messages.loc[:first_occurrence].copy()

    updated_messages_copy = updated_messages.copy()

    return updated_messages_copy


def process_messages(identifier_data, updated_messages, INTERFACE_CONFIG_PD_a):
    try:

        updated_messages_copy = updated_messages.copy()
        logging.debug(f"Before filtering, dimensions of updated_messages_copy: {updated_messages_copy.shape}")

        updated_messages_copy['identifiers_id'] = identifier_data['id']
        updated_messages_copy['gnb_id'] = str(identifier_data['gnb_id'])
        interface_patterns = ['f1ap', 'e1ap', 'ngap', 'xnap']

        updated_messages_copy['interface'] = updated_messages_copy['frame.protocols'].str.extract(
            f"({'|'.join(interface_patterns)})", flags=re.IGNORECASE)
        updated_messages_copy['_ws.col.info_lower'] = updated_messages_copy['_ws.col.info'].str.lower()
        INTERFACE_CONFIG_PD_a['_ws.col.info_lower'] = INTERFACE_CONFIG_PD_a['_ws.col.info'].str.lower()

        merged_messages = pd.merge(updated_messages_copy, INTERFACE_CONFIG_PD_a,
                                   left_on=['_ws.col.info_lower', 'interface'],
                                   right_on=['_ws.col.info_lower', 'interface'], how='left',
                                   suffixes=('_msg', '_config'))

        merged_messages.reset_index(drop=True, inplace=True)
        updated_messages_copy.reset_index(drop=True, inplace=True)

        updated_messages_copy['srcNode'] = merged_messages['srcNode']
        updated_messages_copy['dstNode'] = merged_messages['dstNode']
        # Handle special case for '00000'
        if identifier_data['c_rnti'] == "00000":
            condition1 = (updated_messages_copy['srcNode'] == "CUCP") & (
                    updated_messages_copy['dstNode'] == "Target_CUCP")
            condition2 = (updated_messages_copy['srcNode'] == "Target_CUCP") & (
                    updated_messages_copy['dstNode'] == "CUCP")

            updated_messages_copy.loc[condition1, ['srcNode', 'dstNode']] = ["src_CUCP", "CUCP"]
            updated_messages_copy.loc[condition2, ['srcNode', 'dstNode']] = ["CUCP", "src_CUCP"]

        # Drop the temporary 'interface' column added for merging
        updated_messages_copy.drop(columns=['interface'], inplace=True)
        logging.debug(f"After filtering, dimensions of updated_messages_copy: {updated_messages_copy.shape}")
        updated_messages = updated_messages_copy
        logging.debug(f"After filtering, dimensions of updated_messages: {updated_messages.shape}")
        return updated_messages
    except Exception as e:
        logging.error(f"An error occurred in process_messages: {str(e)}")
        return pd.DataFrame()


def create_message_instances(updated_messages, identifier_data, item_id):
    def create_message(row):
        return {
            'frame_number': row['frame.number'],
            'frame_time': row['frame.time'],
            'ip_src': row['ip.src'],
            'ip_dst': row['ip.dst'],
            'protocol': row['frame.protocols'],
            'f1_proc': row['f1ap.procedureCode'],
            'e1_proc': row['e1ap.procedureCode'],
            'ng_proc': row['ngap.procedureCode'],
            'c1_rrc': row['f1ap.pLMN_Identity'],
            'c2_rrc': row['nr-rrc.ng_5G_S_TMSI_Part1'],
            'mm_message_type': row['nas-5gs.mm.message_type'],
            'sm_message_type': row['nas-5gs.sm.message_type'],
            'message': row['_ws.col.info'],
            'src_node': row["srcNode"],
            'dst_node': row["dstNode"],
            'message_json': None,
            'c_rnti': row['f1ap.C_RNTI'],
            'gnb_du_ue_f1ap_id': row['f1ap.GNB_DU_UE_F1AP_ID'],
            'gnb_cu_ue_f1ap_id': row['f1ap.GNB_CU_UE_F1AP_ID'],
            'gnb_cu_cp_ue_e1ap_id': row['e1ap.GNB_CU_CP_UE_E1AP_ID'],
            'gnb_cu_up_ue_e1ap_id': row['e1ap.GNB_CU_UP_UE_E1AP_ID'],
            'ran_ue_ngap_id': row['ngap.RAN_UE_NGAP_ID'],
            'amf_ue_ngap_id': row['ngap.AMF_UE_NGAP_ID'],
            'xnap_src_ran_id': row['xnap.NG_RANnodeUEXnAPID_src'],
            'xnap_trgt_ran_id': row['xnap.NG_RANnodeUEXnAPID_dst'],
            'uploaded_file_id': item_id,
            'gnb_id': row['gnb_id'],
            'identifiers_id': identifier_data['id'],
            'f1ap_cause': row['f1ap.cause_desc'],
            'ngap_cause': row['ngap.cause_desc'],
            'nas_cause': row['nas.cause_desc']
        }

    try:
        messages = updated_messages.apply(create_message, axis=1)
    except Exception as e:
        logging.error(f"An error occurred in create_message_instances: {str(e)}")

    return messages.tolist()


def create_bulk_update_data(updated_messages, identifier_data):
    try:
        # Create an instance of the computeStats class from statsHandler_sa module
        package_name = 'drawranflow.servicelogic.handlers'
        module_name = 'statsHandler_sa'

        # Import the module dynamically
        module = importlib.import_module(f'.{module_name}', package=package_name)
        compute_stats_class = getattr(module, 'computeStats')

        compute_stats_instance = compute_stats_class()

        # Define functions to run sequentially from the computeStats instance
        functions = [
            compute_stats_instance.calculate_rrc_stats,
            compute_stats_instance.calculate_initial_ctxt_stats,
            compute_stats_instance.calculate_bearerctxt_stats,
            compute_stats_instance.calculate_handover_stats,
            compute_stats_instance.get_cause_data
        ]

        # Create bulk_update_data dictionary
        bulk_update_data = {'id': identifier_data['id']}  # Use dictionary access for identifier_data

        # Execute functions sequentially
        for func_name in functions:
            try:
                # Dynamically import the function
                result = func_name(updated_messages)
                if result is not None:
                    bulk_update_data.update(result)
            except Exception as func_exception:
                logging.error(f"An error occurred in {func_name.__name__}: {str(func_exception)}")

    except Exception as e:
        logging.error(f"An error occurred in create_bulk_update_data: {str(e)}")
        return None

    return bulk_update_data


def bulk_update_identifiers_test(bulk_update_data):
    logging.debug(f"Identifier update with Stats Started. {len(bulk_update_data)}")

    # Ensure a database transaction for bulk updates
    with transaction.atomic():
        try:
            for data in bulk_update_data:
                identifier_id = data['id']
                logging.debug(f"Processing identifier with ID: {identifier_id}, Data: {data}")

                # Use the 'update' method to update existing identifiers
                Identifiers.objects.filter(id=identifier_id).update(**data)

        except Exception as e:
            logging.error(f"Error updating identifiers: {str(e)}")

    logging.debug("Identifier update has been completed!!")


def process_result(sliced_identifiers, shared_messages_to_insert, shared_bulk_update_data, filtered_df, item_id,
                   INTERFACE_CONFIG_PD_a):
    logging.error(f"Process ID {os.getpid()}, Identifier data length: {len(sliced_identifiers)}")

    try:
        for identifier_data in sliced_identifiers:
            logging.debug(
                f"Process ID {os.getpid()}, Identifier data: {identifier_data.get('c_rnti')}, id: {identifier_data.get('id')}")

            filterd_messages = create_filter_conditions(identifier_data, filtered_df)
            if not filterd_messages.empty:
                processed_msgs = process_messages(identifier_data, filterd_messages, INTERFACE_CONFIG_PD_a)
                if not processed_msgs.empty:
                    shared_messages_to_insert.extend(create_message_instances(processed_msgs, identifier_data, item_id))
                    shared_bulk_update_data.append(create_bulk_update_data(processed_msgs, identifier_data))
    except Exception as e:
        logging.error(f"An error occurred in process_result: {str(e)}")
    return shared_messages_to_insert, shared_bulk_update_data
