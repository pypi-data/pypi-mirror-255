import concurrent
from concurrent.futures.thread import ThreadPoolExecutor

import django

from ...models import Messagelte

django.setup()
import logging
import multiprocessing
import os
import re
from functools import partial
from multiprocessing import Manager
from django.utils import timezone
import importlib

import numpy as np
import pandas as pd
from drawranflow.models import Identifierslte, UploadedFile
from .utils_sa import get_gnb_id, get_trgt_gnb_id, INTERFACE_CONFIG_PD
from django.db import IntegrityError, transaction


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

                identifier_object = Identifierslte(
                    c_rnti=c_rnti_value,
                    pci=row.get('pci', None),
                    cucp_f1c_ip=row.get('cucp_f1c_ip', None),
                    du_f1c_ip=row.get('du_f1c_ip', None),
                    gnb_id=row.get('gnb_id', None),
                    uploaded_file_id=row['uploadedFiles_id'],
                    frame_time=row.get('frame_time', None),
                    tmsi=row.get('tmsi', None),
                    plmn=row.get('plmn', None),
                    gtp_teid=row.get('gtp_teid', None),
                    enb_ue_s1ap_id=row.get('enb_ue_s1ap_id', None),
                    mme_ue_s1ap_id=row.get('mme_ue_s1ap_id', None),
                    x2ap_ue_ran_id=row.get('x2ap_ue_ran_id', None),
                    x2ap_5g_ran_id=row.get('x2ap_5g_ran_id', None),
                )

                identifiers_to_create.append(identifier_object)

            except IntegrityError as e:
                logging.error(f"IntegrityError occurred during create: {e}")
            except Exception as e:
                logging.error(f"Error occurred during create: {e}")

            # Bulk create in batches
            if len(identifiers_to_create) >= batch_size:
                Identifierslte.objects.bulk_create(identifiers_to_create)
                identifiers_to_create = []

        # Final bulk create for any remaining objects
        if identifiers_to_create:
            Identifierslte.objects.bulk_create(identifiers_to_create)


def bulk_update_identifiers_test(bulk_update_data):
    logging.debug(f"Identifier update with Stats Started. {len(bulk_update_data)}")

    # Ensure a database transaction for bulk updates
    with transaction.atomic():
        try:
            for data in bulk_update_data:
                identifier_id = data['id']
                logging.debug(f"Processing identifier with ID: {identifier_id}, Data: {data}")

                # Use the 'update' method to update existing identifiers
                Identifierslte.objects.filter(id=identifier_id).update(**data)

        except Exception as e:
            logging.error(f"Error updating identifiers: {str(e)}")

    logging.debug("Identifier update has been completed!!")


def find_messages(df, condition, additional_condition=None):
    try:
        if additional_condition is None:
            return df[condition]
        else:
            return df[condition & additional_condition]
    except Exception as e:
        logging.error(f"Error occurred during message retrieval: {e}")
        return pd.DataFrame()


# THis is for NSA call flow
def message_handler(df, item_id):
    try:
        upload_table = UploadedFile.objects.get(id=item_id)
        logging.error(f"Preparing initial analysis for the NSA, pcap file: {upload_table.filename}")

        lte_df = filter_dataframe_by_protocol(df, 'lte_rrc')
        s1ap_df = filter_dataframe_by_protocol(df, 's1ap')
        x2ap_df = filter_dataframe_by_protocol(df, 'x2ap')
        s1ap_df.loc[:, 's1ap.ENB_UE_S1AP_ID'] = s1ap_df['s1ap.ENB_UE_S1AP_ID'].apply(split_values)

        # Find RRC Setup, Reestablishment, and Setup Request messages
        rrc_setup_df = lte_df[lte_df['_ws.col.info'] == 'RRCConnectionSetup']
        rrc_reestablish_res_df = lte_df[lte_df['_ws.col.info'] == 'RRC Reestablishment']
        rrc_setup_request_df = lte_df[
            (lte_df['_ws.col.info'] == 'RRCConnectionRequest') & ~lte_df['mavlterrc.rnti'].isnull()]
        rrc_reestablish_df = lte_df[
            (lte_df['_ws.col.info'] == 'RRC Reestablishment Request') & ~lte_df['mavlterrc.rnti'].isnull()]

        combined_df = pd.concat([rrc_setup_request_df, rrc_reestablish_df])

        service_request_df = s1ap_df[
            ((s1ap_df['_ws.col.info'] == 'Service request')
             | (s1ap_df['_ws.col.info'] == 'PDN connectivity request')
             | (s1ap_df['_ws.col.info'] == 'Tracking area update request')) & ~s1ap_df['s1ap.ENB_UE_S1AP_ID'].isnull()
            ]
        service_request_df.loc[:, 's1ap.CellIdentity'] = combined_df['s1ap.CellIdentity'].map(get_gnb_id)

        s1ap_initial_messages_df = s1ap_df[
            ((s1ap_df['_ws.col.info'] == 'InitialContextSetupRequest') |
             (s1ap_df['_ws.col.info'] == 'Activate default EPS bearer context request') |
             (s1ap_df['_ws.col.info'] == 'UECapabilityInformation') |
             (s1ap_df['_ws.col.info'] == 'Identity request') |
             (s1ap_df['_ws.col.info'] == 'Authentication request') |
             (s1ap_df['_ws.col.info'] == 'Security mode command') |
             (s1ap_df['_ws.col.info'] == 'ESM Information request') |
             (s1ap_df['_ws.col.info'] == 'Registration Reject') |
             (s1ap_df['_ws.col.info'].str.contains('Registration reject')) |
             (s1ap_df['_ws.col.info'] == 'PDU Session Setup Request')) &
            ~s1ap_df['s1ap.ENB_UE_S1AP_ID'].isnull() &
            ~s1ap_df['s1ap.MME_UE_S1AP_ID'].isnull()
            ]

        logging.debug(f"s1ap_initial_messages_df {s1ap_initial_messages_df}")
        s1ap_act_bearer_req_df = s1ap_df[
            ((s1ap_df['_ws.col.info'] == 'InitialContextSetupRequest') |
             (s1ap_df['_ws.col.info'] == 'Activate default EPS bearer context request')) &
            ~s1ap_df['s1ap.ENB_UE_S1AP_ID'].isnull() &
            ~s1ap_df['s1ap.MME_UE_S1AP_ID'].isnull()
            ]
        x2ap_gnb_addition_df = x2ap_df[
            (x2ap_df['_ws.col.info'] == 'SgNBAdditionRequest') &
            ~x2ap_df['x2ap.UE_X2AP_ID'].isnull() &
            x2ap_df['x2ap.SgNB_UE_X2AP_ID'].isnull()
            ]

        x2ap_gnb_addition_res_df = x2ap_df[
            (x2ap_df['_ws.col.info'] == 'RRC Reconfiguration') |
            (x2ap_df['_ws.col.info'] == 'SgNBAdditionRequestAcknowledge') &
            ~x2ap_df['x2ap.UE_X2AP_ID'].isnull() &
            ~x2ap_df['x2ap.SgNB_UE_X2AP_ID'].isnull()
            ]
        # Define the column mapping
        column_name_mapping = {
            'mavlterrc.rnti': 'c_rnti',
            'mavlterrc.cellid': 'pci',
            'frame.time': 'frame_time',
            's1ap.ENB_UE_S1AP_ID': 'enb_ue_s1ap_id',
            's1ap.MME_UE_S1AP_ID': 'mme_ue_s1ap_id',
            'ip.src': 'du_f1c_ip',
            'ip.dst': 'cucp_f1c_ip',
            'x2ap.UE_X2AP_ID': 'x2ap_ue_ran_id',
            'x2ap.SgNB_UE_X2AP_ID': 'x2ap_5g_ran_id',
            's1ap.CellIdentity': 'gnb_id',
            'nas_eps.emm.m_tmsi': 'tmsi',
            's1ap.pLMN_Identity': 'plmn',
        }

        identifiers_df = combined_df[list(column_name_mapping.keys())].copy()
        # Map 'xnap.NR_Cell_Identity' to 'gnb_id' in xnap_df
        x2ap_gnb_addition_df.loc[:, 'x2ap.eUTRANcellIdentifier'] = x2ap_gnb_addition_df[
            'x2ap.eUTRANcellIdentifier'].map(get_trgt_gnb_id).astype(str)

        # Copy relevant columns from combined_df to identifiers_df
        identifiers_df.rename(columns=column_name_mapping, inplace=True)

        # Save to Identifiers table
        identifiers_df['uploadedFiles_id'] = item_id
        manager = Manager()
        shared_identifiers_df = manager.list(identifiers_df.to_dict('records'))

        num_processes = min(multiprocessing.cpu_count(), len(shared_identifiers_df))
        chunk_size = max(1, len(identifiers_df) // num_processes)

        with multiprocessing.Pool(num_processes) as pool, multiprocessing.Manager() as manager:
            dataframe_dict = {

                'rrc_setup_df': rrc_setup_df,
                'service_request_df': service_request_df,
                's1ap_initial_messages_df': s1ap_initial_messages_df,
                's1ap_act_bearer_req_df': s1ap_act_bearer_req_df,
                'x2ap_gnb_addition_df': x2ap_gnb_addition_df,
                'x2ap_gnb_addition_res_df': x2ap_gnb_addition_res_df,

            }
            results = pool.map(partial(process_slice, dataframes=dataframe_dict),
                               chunks(shared_identifiers_df, chunk_size))

        # Concatenate the processed data from the shared list
        combined_df = pd.concat(results)
        logging.debug(f"combined_df :{combined_df}")
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


def deriveIdentifiers(identifier_row, df_slice, rrc_setup_df, service_request_df,
                      s1ap_initial_messages_df, s1ap_act_bearer_req_df, x2ap_gnb_addition_df, x2ap_gnb_addition_res_df,
                      index):
    def update_identifiers(identifier_df, match_df, column_name, actualcolumn, identifier_row, index):
        try:
            logging.debug(f"update_identifiers: {identifier_row['c_rnti']} - {column_name} - {actualcolumn}")
            logging.debug(f"match_df: {match_df}")

            new_value = match_df.iloc[0][actualcolumn]
            identifier_df.at[index, column_name] = str(new_value)
            logging.debug(f"Updated {column_name} to {new_value}")
            return new_value
        except IndexError:
            logging.warning(f"IndexError during identifier update.")
            return None
        except Exception as e:
            logging.error(f"Error occurred during identifier update: {e}")
            return None

    def update_identifiers_gtp(identifier_df, match_df, column_name, actualcolumn, identifier_row, index):
        try:
            logging.debug(f"update_identifiers: {identifier_row['c_rnti']} - {column_name} - {actualcolumn}")
            logging.debug(f"match_df: {match_df}")

            first_valid_index = match_df[actualcolumn].first_valid_index()
            if first_valid_index is None:
                logging.warning(f"No valid value for {actualcolumn}.")
                return None

            new_value = match_df.loc[first_valid_index, actualcolumn]
            identifier_df.at[index, column_name] = str(new_value)
            logging.debug(f"Updated {column_name} to {new_value}")
            return new_value
        except IndexError:
            logging.warning(f"IndexError during identifier update.")
            return None
        except Exception as e:
            logging.error(f"Error occurred during identifier update: {e}")
            return None

    try:
        logging.debug(f"identifier_row: {identifier_row}")
        identifier_time = pd.to_datetime(identifier_row['frame_time'], utc=True)
        identifier_crnti = identifier_row['c_rnti']
        identifier_du_ip = identifier_row['du_f1c_ip']
        identifier_cucp_ip = identifier_row['cucp_f1c_ip']
        logging.debug(f"----: {identifier_time} {identifier_crnti} {identifier_du_ip} {identifier_cucp_ip}")

        if identifier_crnti is not None and not pd.isnull(identifier_crnti):
            logging.debug(f"inside if block: {identifier_crnti}")
            matching_lte_rrc_setup = find_messages(
                rrc_setup_df,
                (rrc_setup_df['frame.time'] > identifier_time) &
                (rrc_setup_df['frame.time'] <= identifier_time + pd.Timedelta('2s')) &
                (rrc_setup_df['ip.src'] == identifier_cucp_ip) &
                (rrc_setup_df['ip.dst'] == identifier_du_ip) &
                (rrc_setup_df['mavlterrc.rnti'] == identifier_row['c_rnti']) &
                (rrc_setup_df['mavlterrc.cellid'] == identifier_row['pci'])
            )
            if not matching_lte_rrc_setup.empty:
                matching_s1ap_setup = find_messages(
                    service_request_df,
                    (service_request_df['frame.time'] >= identifier_row['frame_time']) &
                    (service_request_df['frame.time'] <= identifier_time + pd.Timedelta('2s'))

                )

                # Update ran_ue_ngap_id in the Identifier DataFrame
                enb_ue_s1ap_id = update_identifiers(df_slice, matching_s1ap_setup, 'enb_ue_s1ap_id',
                                                    's1ap.ENB_UE_S1AP_ID', identifier_row, index)
                update_identifiers(df_slice, matching_s1ap_setup, 'tmsi',
                                   'nas_eps.emm.m_tmsi', identifier_row, index)
                logging.debug(f"s1ap_initial_messages_df, {s1ap_initial_messages_df}")
                matching_s1ap_ictxt_setup = find_messages(s1ap_initial_messages_df,
                                                          (s1ap_initial_messages_df['frame.time'] >=
                                                           identifier_time) &
                                                          (s1ap_initial_messages_df['frame.time'] <=
                                                           identifier_time + pd.Timedelta('1s')) &
                                                          (s1ap_initial_messages_df[
                                                               's1ap.ENB_UE_S1AP_ID'] == enb_ue_s1ap_id))
                logging.debug(f"matching_s1ap_ictxt_setup {matching_s1ap_ictxt_setup}")
                # Update amf_ue_ngap_id using the update_identifiers function
                mme_ue_s1ap_id = update_identifiers(df_slice, matching_s1ap_ictxt_setup,
                                                    'mme_ue_s1ap_id',
                                                    's1ap.MME_UE_S1AP_ID', identifier_row, index)

                gtp_eid = update_identifiers_gtp(df_slice, matching_s1ap_ictxt_setup, 'gtp_teid',
                                                 's1ap.gTP_TEID', identifier_row, index)
                if gtp_eid == np.nan or gtp_eid == "nan" or gtp_eid is None:
                    logging.debug(f"s1ap_act_bearer_req_df {s1ap_act_bearer_req_df}")
                    matching_act_bearer = find_messages(s1ap_act_bearer_req_df,
                                                        (s1ap_act_bearer_req_df['frame.time'] >=
                                                         identifier_time) &
                                                        (s1ap_act_bearer_req_df['frame.time'] <=
                                                         identifier_time + pd.Timedelta('1s')) &
                                                        (s1ap_act_bearer_req_df[
                                                             's1ap.ENB_UE_S1AP_ID'] == enb_ue_s1ap_id) &
                                                        (s1ap_act_bearer_req_df[
                                                             's1ap.MME_UE_S1AP_ID'] == mme_ue_s1ap_id)
                                                        )
                    gtp_eid = update_identifiers_gtp(df_slice, matching_act_bearer, 'gtp_teid',
                                                     's1ap.gTP_TEID', identifier_row, index)
                    logging.debug(f"matching_act_bearer: {matching_act_bearer}")
                logging.debug(
                    f"row: {index},enb_ue_s1ap_id: {enb_ue_s1ap_id}, mme_ue_s1ap_id: {mme_ue_s1ap_id},gtp_eid:{gtp_eid}")

                matching_x2ap_req_setup = find_messages(x2ap_gnb_addition_df,
                                                        (x2ap_gnb_addition_df['frame.time'] >=
                                                         identifier_time) &
                                                        (x2ap_gnb_addition_df['frame.time'] <=
                                                         identifier_time + pd.Timedelta("10s")) &
                                                        (x2ap_gnb_addition_df[
                                                             'x2ap.gTP_TEID'].str.contains(gtp_eid)))

                # Update xnap_src_ran_id using the update_identifier_and_log function
                x2ap_ue_ran_id = update_identifiers(df_slice, matching_x2ap_req_setup,
                                                    'x2ap_ue_ran_id',
                                                    'x2ap.UE_X2AP_ID', identifier_row, index)
                logging.debug(f"row: {index},x2ap_ue_ran_id:{x2ap_ue_ran_id}")

                matching_x2ap_resp_setup = find_messages(x2ap_gnb_addition_res_df,
                                                         (x2ap_gnb_addition_res_df['frame.time'] >=
                                                          identifier_time) &
                                                         (x2ap_gnb_addition_res_df[
                                                              'x2ap.UE_X2AP_ID'] == x2ap_ue_ran_id))

                # Update xnap_trgt_ran_id using the update_identifier_and_log function
                update_identifiers(df_slice, matching_x2ap_resp_setup, 'x2ap_5g_ran_id',
                                   'x2ap.SgNB_UE_X2AP_ID', identifier_row, index)

                return df_slice
    except Exception as e:
        logging.error(f"Error occurred during row processing: {e}")


def process_slice(slice_data, dataframes=None):
    global df_slice
    rrc_setup_df = dataframes.get('rrc_setup_df')
    service_request_df = dataframes.get('service_request_df')
    s1ap_initial_messages_df = dataframes.get('s1ap_initial_messages_df')
    s1ap_act_bearer_req_df = dataframes.get('s1ap_act_bearer_req_df')
    x2ap_gnb_addition_df = dataframes.get('x2ap_gnb_addition_df')
    x2ap_gnb_addition_res_df = dataframes.get('x2ap_gnb_addition_res_df')

    try:
        if isinstance(slice_data, dict):

            df_slice = pd.DataFrame([slice_data]).astype({
                'c_rnti': str,
                'pci': str,
                'frame_time': str,
                'enb_ue_s1ap_id': str,
                'mme_ue_s1ap_id': str,
                'du_f1c_ip': str,
                'cucp_f1c_ip': str,
                'x2ap_ue_ran_id': str,
                'x2ap_5g_ran_id': str,
                'gnb_id': str,
                'tmsi': str,
                'plmn': str,
            })
        elif isinstance(slice_data, list):
            # If slice_data is a list of dictionaries, convert it to a DataFrame
            df_slice = pd.DataFrame(slice_data).astype({
                'c_rnti': str,
                'pci': str,
                'frame_time': str,
                'enb_ue_s1ap_id': str,
                'mme_ue_s1ap_id': str,
                'du_f1c_ip': str,
                'cucp_f1c_ip': str,
                'x2ap_ue_ran_id': str,
                'x2ap_5g_ran_id': str,
                'gnb_id': str,
                'tmsi': str,
                'plmn': str,
            })
        for index, identifier_row in df_slice.iterrows():
            try:
                logging.debug(f"Process ID {os.getpid()}: identifier_row: {identifier_row}")

                identifier_crnti = identifier_row['c_rnti']
                if identifier_crnti != "nan":
                    deriveIdentifiers(identifier_row, df_slice, rrc_setup_df, service_request_df,
                                      s1ap_initial_messages_df, s1ap_act_bearer_req_df, x2ap_gnb_addition_df,
                                      x2ap_gnb_addition_res_df, index)

            except Exception as e:
                logging.error(f"Process ID {os.getpid()}: Error occurred during row processing: {e}")
    except Exception as e:
        logging.error(f"Process ID {os.getpid()}: Error occurred during row processing: {e}")
    logging.debug(f"Process ID {os.getpid()}: Exiting process_slice")
    return df_slice


def fetch_identifier_data(row_id):
    logging.debug(f'identifier_data in fetch_identifier_data: {row_id}')
    identifier_data = Identifierslte.objects.get(id=row_id)

    return identifier_data


def filter_pcap(input_file, filter_string, output_file):
    capture = pyshark.FileCapture(input_file, display_filter=f"{filter_string}", output_file=f'{output_file}')
    capture.set_debug()
    filtered_packets = [packet for packet in capture]
    logging.debug(f'filtered_packets,{filtered_packets} - output: {output_file}, filterString:{filter_string}')

    return output_file


def update_messages_with_identifier_key(df, item_id):
    try:
        with transaction.atomic():
            upload_table = UploadedFile.objects.get(id=item_id)
            logging.error(f"Started filtering messages for each call flow: {upload_table.filename}")

            # The columns to check for undesired values
            columns_to_check = [
                'mavlterrc.rnti',
                'mavlterrc.cellid',
                's1ap.ENB_UE_S1AP_ID',
                's1ap.MME_UE_S1AP_ID',
                'e212.imsi',
                's1ap.CellIdentity',
                'x2ap.eUTRANcellIdentifier',
                'x2ap.UE_X2AP_ID',
                'x2ap.SgNB_UE_X2AP_ID',
                's1ap.pLMN_Identity',
                'x2ap.gTP_TEID',
                's1ap.gTP_TEID',
            ]

            # Specify undesired values
            undesired_values = ["none", "nan", "", None, "NaN", np.nan]

            # Create a mask to filter out rows with undesired values in the specified columns
            mask = df[columns_to_check].apply(
                lambda col: ~col.astype(str).str.lower().isin(undesired_values)
            )

            filtered_df = df[mask.any(axis=1)]
            identifiers = Identifierslte.objects.filter(uploaded_file_id=item_id).values()
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
            logging.debug(shared_bulk_update_data)
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
                    concurrent.futures.wait(future_update + [futures_create], timeout=None,
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
    except Exception as e:
        logging.error(f"Exception during update_messages_with_identifier_key: {e}")
        pass
    finally:
        pool.terminate()
        manager.shutdown()


def bulk_create_messages(chunk):
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Use ThreadPoolExecutor to parallelize message instance creation
            message_instances = list(executor.map(create_message_instance, chunk))

        # Bulk create messages
        Messagelte.objects.bulk_create(message_instances)

    except Exception as e:
        logging.error(f"Error in processing bulk_create_messages {e}")


def create_message_instance(row):
    return Messagelte(
        frame_number=row['frame_number'],
        frame_time=row['frame_time'],
        ip_src=row['ip_src'],
        ip_dst=row['ip_dst'],
        protocol=row['protocol'],
        message=row['message'],
        src_node=row["src_node"],
        dst_node=row["dst_node"],
        message_json=None,
        c_rnti=row['c_rnti'],
        enb_ue_s1ap_id=row['enb_ue_s1ap_id'],
        mme_ue_s1ap_id=row['mme_ue_s1ap_id'],
        x2ap_ue_ran_id=row['x2ap_ue_ran_id'],
        x2ap_5g_ran_id=row['x2ap_5g_ran_id'],
        identifiers_id=row['identifiers_id'],
        s1ap_cause=row['s1ap_cause'],
        uploaded_file_id=row['uploaded_file_id'],
        nas_cause=row['nas_cause'],
        x2ap_cause=row['x2ap_cause'],
    )


def create_filter_conditions(identifier_data, filtered_df):
    two_sec = pd.Timedelta(minutes=10)

    filter_conditions = pd.Series(False, index=filtered_df.index)
    if identifier_data["c_rnti"] != 'nan' and identifier_data["pci"] != 'nan' and identifier_data["c_rnti"] != '00000':
        filter_conditions |= ((filtered_df['mavlterrc.rnti'] == identifier_data["c_rnti"])
                              & (filtered_df['mavlterrc.cellid'] == identifier_data["pci"])
                              & (filtered_df['frame.time'] <= identifier_data["frame_time"] + two_sec))

    if identifier_data["enb_ue_s1ap_id"] != 'nan' and identifier_data["mme_ue_s1ap_id"] != 'nan':
        filter_conditions |= (((filtered_df['s1ap.ENB_UE_S1AP_ID'] == identifier_data["enb_ue_s1ap_id"]) &
                               (filtered_df['frame.time'] > identifier_data["frame_time"])) |
                              ((filtered_df['s1ap.ENB_UE_S1AP_ID'] == identifier_data["enb_ue_s1ap_id"]) &
                               (filtered_df['s1ap.MME_UE_S1AP_ID'] == identifier_data["mme_ue_s1ap_id"]) &
                               (filtered_df['frame.time'] > identifier_data["frame_time"])))

    if identifier_data["enb_ue_s1ap_id"] != 'nan' and identifier_data["mme_ue_s1ap_id"] == 'nan':
        filter_conditions |= (filtered_df[
                                  's1ap.ENB_UE_S1AP_ID'] == identifier_data["enb_ue_s1ap_id"]) \
                             & (filtered_df['s1ap.MME_UE_S1AP_ID'].isna() & (
                filtered_df['frame.time'] > identifier_data["frame_time"]))

    if identifier_data["x2ap_ue_ran_id"] != 'nan' and identifier_data["x2ap_5g_ran_id"] != 'nan':
        filter_conditions |= (((filtered_df['x2ap.UE_X2AP_ID'] == identifier_data["x2ap_ue_ran_id"]) &
                               (filtered_df['frame.time'] > identifier_data["frame_time"])) |
                              ((filtered_df['x2ap.UE_X2AP_ID'] == identifier_data["x2ap_ue_ran_id"]) &
                               (filtered_df['x2ap.SgNB_UE_X2AP_ID'] == identifier_data["x2ap_5g_ran_id"])) &
                              (filtered_df['frame.time'] > identifier_data["frame_time"]))

    if identifier_data["x2ap_ue_ran_id"] != 'nan' and identifier_data["x2ap_5g_ran_id"] == 'nan':
        filter_conditions |= (filtered_df[
                                  'ex2ap.UE_X2AP_ID'] == identifier_data["x2ap_ue_ran_id"]) \
                             & (filtered_df['x2ap.SgNB_UE_X2AP_ID'].isna() & (
                filtered_df['frame.time'] > identifier_data["frame_time"]))

    updated_messages = filtered_df[filter_conditions]
    condition = ((updated_messages['_ws.col.info'] == 'UEContextReleaseComplete') &
                 updated_messages['frame.protocols'].str.contains('s1ap'))

    if condition.any():  # If the condition is met at least once
        first_occurrence = condition.idxmax()

        updated_messages = updated_messages.loc[:first_occurrence + 4].copy()

    updated_messages_copy = updated_messages.copy()

    return updated_messages_copy


def process_messages(identifier_data, updated_messages, INTERFACE_CONFIG_PD_a):
    try:

        updated_messages_copy = updated_messages.copy()
        logging.debug(f"Before filtering, dimensions of updated_messages_copy: {updated_messages_copy.shape}")

        updated_messages_copy['identifiers_id'] = identifier_data['id']
        # updated_messages_copy['gnb_id'] = str(identifier_data.gnb_id)
        interface_patterns = ['s1ap', 'x2ap', 'lte_rrc']

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
        if identifier_data["c_rnti"] == "00000":
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
    global messages

    def create_message(row):
        return {
            'frame_number': row['frame.number'],
            'frame_time': row['frame.time'],
            'ip_src': row['ip.src'],
            'ip_dst': row['ip.dst'],
            'protocol': row['frame.protocols'],
            'message': row['_ws.col.info'],
            'src_node': row['srcNode'],
            'dst_node': row['dstNode'],
            'message_json': None,
            'c_rnti': row['mavlterrc.rnti'],
            'enb_ue_s1ap_id': row['s1ap.ENB_UE_S1AP_ID'],
            'mme_ue_s1ap_id': row['s1ap.MME_UE_S1AP_ID'],
            'x2ap_ue_ran_id': row['x2ap.UE_X2AP_ID'],
            'x2ap_5g_ran_id': row['x2ap.SgNB_UE_X2AP_ID'],
            'uploaded_file_id': item_id,
            'gnb_id': np.nan,
            'identifiers_id': identifier_data['id'],
            's1ap_cause': row.get('s1ap.cause_desc', None),
            'nas_cause': row.get('nas.cause_desc', None),
            'x2ap_cause': row.get('x2ap.cause_desc', None)
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
        module_name = 'statsHandler_lte'

        # Import the module dynamically
        module = importlib.import_module(f'.{module_name}', package=package_name)
        compute_stats_class = getattr(module, 'computeStats')

        compute_stats_instance = compute_stats_class()

        # Define functions to run sequentially from the computeStats instance
        functions = [
            compute_stats_instance.calculate_rrc_stats,
            compute_stats_instance.calculate_initial_ctxt_stats,
            compute_stats_instance.calculate_pdn_stats,
            compute_stats_instance.calculate_x2ap_handover_stats,
            compute_stats_instance.calculate_s1ap_handover_stats,
            compute_stats_instance.calculate_x2ap_sgNBadd_stats

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


def bulk_update_identifiers_t(bulk_update_data):
    logging.error(f"Identifier update with Stats Started. {len(bulk_update_data)}")

    for data in bulk_update_data:
        identifier_id = data['id']
        Identifierslte.objects.update_or_create(
            id=identifier_id,
            defaults=data,
        )
    logging.error(f"Identifier update has been completed!!")


def process_result(sliced_identifiers, shared_messages_to_insert, shared_bulk_update_data, filtered_df, item_id,
                   INTERFACE_CONFIG_PD_a):
    logging.error(f"Process ID {os.getpid()}, Identifier data length: {len(sliced_identifiers)}")

    try:
        for identifier_data in sliced_identifiers:
            logging.debug(f"entifier_data {identifier_data}")
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
