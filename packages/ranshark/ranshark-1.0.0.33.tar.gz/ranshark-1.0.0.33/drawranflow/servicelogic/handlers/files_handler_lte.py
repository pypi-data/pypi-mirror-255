from concurrent import futures

from django.core.paginator import Paginator
from django.db import transaction

from drawranflow.models import UploadedFile, Identifierslte, Messagelte
import pyshark
import os
from django.conf import settings
import logging
import pandas as pd
import numpy as np
from .utils_sa import INTERFACE_CONFIG_PD
import re
from .statsHandler_lte import computeStats as sh
import concurrent


class FileHandlers:
    def __init__(self):
        pass

    MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', None)

    @classmethod
    def upload_pcap_file(cls, file, network):
        file_path = os.path.join(settings.MEDIA_ROOT, file.name)

        # Try to get an existing UploadedFile record with the same filename
        try:
            upload_table = UploadedFile.objects.get(filename=file.name)

            # If it exists, delete associated records and the UploadedFile record
            Identifierslte.objects.filter(uploaded_file__id=upload_table.id).delete()
            Messagelte.objects.filter(
                identifiers__id__in=Identifierslte.objects.filter(uploaded_file__id=upload_table.id).values(
                    'id')).delete()
            upload_table.delete()

            # Remove the file from the file system
            if os.path.exists(file_path):
                cls.delete_files(file_path)
        except UploadedFile.DoesNotExist:
            pass

        # Save the new file
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # Create or update the UploadedFile record
        uploaded_file_record, created = UploadedFile.objects.get_or_create(filename=file.name, processed=False,
                                                                           network=network)
        uploaded_file_record.save()

        if uploaded_file_record:
            messages = {
                'message_type': 'success',
                'message_text': 'File uploaded successfully',
            }
        else:
            messages = {
                'message_type': 'error',
                'message_text': 'File upload failed',
            }

        return messages

    @classmethod
    def delete_files(cls, file_path):
        # Remove the main file
        os.remove(file_path)
        file_prefix = os.path.basename(file_path).split('.')[0]

        # Find and delete associated files with the same prefix
        for file_name in os.listdir(settings.MEDIA_ROOT):
            if file_name.startswith(file_prefix):
                file_to_delete = os.path.join(settings.MEDIA_ROOT, file_name)
                logging.debug(f"Deleting file: {file_to_delete}")
                os.remove(file_to_delete)

    @classmethod
    def construct_pcap_filter(cls, identifier_data):
        filter_conditions = []
        if identifier_data.c_rnti != 'nan' and identifier_data.pci != 'nan' and identifier_data.c_rnti != '00000':
            filter_conditions.append(f"(mavlterrc.rnti=={identifier_data.c_rnti} && "
                                     f"mavlterrc.cellid=={identifier_data.pci})")

        if identifier_data.enb_ue_s1ap_id != 'nan' and identifier_data.mme_ue_s1ap_id != 'nan':
            filter_conditions.append(f"(s1ap.ENB_UE_S1AP_ID=={identifier_data.enb_ue_s1ap_id}) ||"
                                     f" (s1ap.ENB_UE_S1AP_ID=={identifier_data.enb_ue_s1ap_id} &&"
                                     f" s1ap.MME_UE_S1AP_ID=={identifier_data.mme_ue_s1ap_id})")

        if identifier_data.enb_ue_s1ap_id != 'nan' and identifier_data.mme_ue_s1ap_id == 'nan':
            filter_conditions.append(f"(s1ap.ENB_UE_S1AP_ID=={identifier_data.enb_ue_s1ap_id})")

        if identifier_data.x2ap_ue_ran_id != 'nan' and identifier_data.x2ap_5g_ran_id != 'nan':
            filter_conditions.append(f"(x2ap.UE_X2AP_ID=={identifier_data.x2ap_ue_ran_id}) ||"
                                     f" (x2ap.UE_X2AP_ID=={identifier_data.x2ap_ue_ran_id} &&"
                                     f" x2ap.SgNB_UE_X2AP_ID=={identifier_data.x2ap_5g_ran_id})")

        if identifier_data.x2ap_ue_ran_id != 'nan' and identifier_data.x2ap_5g_ran_id == 'nan':
            filter_conditions.append(f"(ex2ap.UE_X2AP_ID=={identifier_data.x2ap_ue_ran_id})")

        filter_string = " or ".join(filter_conditions)
        logging.debug(f'Filter string - {filter_string}')
        # Log or use the generated filter_string as needed

        return filter_string

    @classmethod
    def fetch_identifier_data(cls, row_id):
        logging.debug(f'identifier_data in fetch_identifier_data: {row_id}')
        identifier_data = Identifierslte.objects.get(id=row_id)

        return identifier_data

    @classmethod
    def filter_pcap(cls, input_file, filter_string, output_file):
        capture = pyshark.FileCapture(input_file, display_filter=f"{filter_string}", output_file=f'{output_file}')
        capture.set_debug()
        filtered_packets = [packet for packet in capture]
        logging.debug(f'filtered_packets,{filtered_packets} - output: {output_file}, filterString:{filter_string}')

        return output_file

    @classmethod
    def update_messages_with_identifier_key(cls, df, item_id):
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
                identifiers = Identifierslte.objects.filter(uploaded_file_id=item_id)

                messages_to_insert = []
                bulk_update_data = []

                # Use ThreadPoolExecutor to process messages concurrently for each identifier
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = []
                    for identifier_data in identifiers:

                        logging.debug(f"Identifier data: {identifier_data.c_rnti}, id: {identifier_data.id}")
                        filter_conditions = cls.create_filter_conditions(identifier_data, filtered_df)

                        updated_messages = filter_conditions
                        future = executor.submit(cls.process_messages, identifier_data, updated_messages, messages_to_insert, bulk_update_data, item_id)
                        futures.append(future)

                        # Wait for all futures to complete
                        concurrent.futures.wait(futures, timeout=None, return_when=concurrent.futures.ALL_COMPLETED)

                batch_size = 400
                total_messages = len(messages_to_insert)
                logging.error(f"Messages filter has been completed : {total_messages}")

                logging.error(f"total_messages to insert : {total_messages}")

                for start in range(0, total_messages, batch_size):
                    end = start + batch_size
                    current_batch = messages_to_insert[start:end]

                    # Bulk insert the current batch
                    Messagelte.objects.bulk_create(current_batch)
                logging.error(f"Messages insertion has been completed!!")

                cls.bulk_update_identifiers(bulk_update_data)

        except Exception as e:
            logging.error(f"Exception during update_messages_with_identifier_key: {e}")
            pass

    @classmethod
    def create_filter_conditions(cls, identifier_data, filtered_df):
        two_sec = pd.Timedelta(minutes=10)

        filter_conditions = pd.Series(False, index=filtered_df.index)
        if identifier_data.c_rnti != 'nan' and identifier_data.pci != 'nan' and identifier_data.c_rnti != '00000':
            filter_conditions |= ((filtered_df['mavlterrc.rnti'] == identifier_data.c_rnti)
            & (filtered_df['mavlterrc.cellid'] == identifier_data.pci)
            & (filtered_df['frame.time'] <= identifier_data.frame_time + two_sec))

        if identifier_data.enb_ue_s1ap_id != 'nan' and identifier_data.mme_ue_s1ap_id != 'nan':
                    filter_conditions |= (((filtered_df['s1ap.ENB_UE_S1AP_ID'] == identifier_data.enb_ue_s1ap_id) &
                                           (filtered_df['frame.time'] > identifier_data.frame_time)) |
                                          ((filtered_df['s1ap.ENB_UE_S1AP_ID'] == identifier_data.enb_ue_s1ap_id) &
                                           (filtered_df['s1ap.MME_UE_S1AP_ID'] == identifier_data.mme_ue_s1ap_id)) &
                                          (filtered_df['frame.time'] > identifier_data.frame_time))

        if identifier_data.enb_ue_s1ap_id != 'nan' and identifier_data.mme_ue_s1ap_id == 'nan':
                    filter_conditions |= (filtered_df[
                                              's1ap.ENB_UE_S1AP_ID'] == identifier_data.enb_ue_s1ap_id) \
                                         & (filtered_df['s1ap.MME_UE_S1AP_ID'].isna() & (
                            filtered_df['frame.time'] > identifier_data.frame_time))

        if identifier_data.x2ap_ue_ran_id != 'nan' and identifier_data.x2ap_5g_ran_id != 'nan':
                    filter_conditions |= (((filtered_df['x2ap.UE_X2AP_ID'] == identifier_data.x2ap_ue_ran_id) &
                                           (filtered_df['frame.time'] > identifier_data.frame_time)) |
                                          ((filtered_df['x2ap.UE_X2AP_ID'] == identifier_data.x2ap_ue_ran_id) &
                                           (filtered_df['x2ap.SgNB_UE_X2AP_ID'] == identifier_data.x2ap_5g_ran_id)) &
                                          (filtered_df['frame.time'] > identifier_data.frame_time))

        if identifier_data.x2ap_ue_ran_id != 'nan' and identifier_data.x2ap_5g_ran_id == 'nan':
                    filter_conditions |= (filtered_df[
                                              'ex2ap.UE_X2AP_ID'] == identifier_data.x2ap_ue_ran_id) \
                                         & (filtered_df['x2ap.SgNB_UE_X2AP_ID'].isna() & (
                            filtered_df['frame.time'] > identifier_data.frame_time))

        updated_messages = filtered_df[filter_conditions]
        condition = ((updated_messages['_ws.col.info'] == 'UEContextReleaseComplete') &
                             updated_messages['frame.protocols'].str.contains('s1ap'))

        if condition.any():  # If the condition is met at least once
            first_occurrence = condition.idxmax()

            updated_messages = updated_messages.loc[:first_occurrence + 4].copy()

        updated_messages_copy = updated_messages.copy()

        return updated_messages_copy

    @classmethod
    def process_messages(cls, identifier_data, updated_messages, messages_to_insert, bulk_update_data, item_id):
        try:

            updated_messages_copy = updated_messages.copy()
            logging.debug(f"Before filtering, dimensions of updated_messages_copy: {updated_messages_copy.shape}")

            updated_messages_copy['identifiers_id'] = identifier_data.id
            #updated_messages_copy['gnb_id'] = str(identifier_data.gnb_id)
            interface_patterns = ['s1ap', 'x2ap', 'lte_rrc']

            updated_messages_copy['interface'] = updated_messages_copy['frame.protocols'].str.extract(
                f"({'|'.join(interface_patterns)})", flags=re.IGNORECASE)

            updated_messages_copy['_ws.col.info_lower'] = updated_messages_copy['_ws.col.info'].str.lower()
            INTERFACE_CONFIG_PD['_ws.col.info_lower'] = INTERFACE_CONFIG_PD['_ws.col.info'].str.lower()

            merged_messages = pd.merge(updated_messages_copy, INTERFACE_CONFIG_PD,
                                       left_on=['_ws.col.info_lower', 'interface'],
                                       right_on=['_ws.col.info_lower', 'interface'], how='left',
                                       suffixes=('_msg', '_config'))

            merged_messages.reset_index(drop=True, inplace=True)
            updated_messages_copy.reset_index(drop=True, inplace=True)

            updated_messages_copy['srcNode'] = merged_messages['srcNode']
            updated_messages_copy['dstNode'] = merged_messages['dstNode']
            # Handle special case for '00000'
            if identifier_data.c_rnti == "00000":
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
            messages_to_insert.extend(cls.create_message_instances(updated_messages, identifier_data, item_id))
            bulk_update_data.append(cls.create_bulk_update_data(updated_messages, identifier_data))

        except Exception as e:
            logging.error(f"An error occurred in process_messages: {str(e)}")

   
    @classmethod
    def create_message_instances(cls, updated_messages, identifier_data, item_id):

        def create_message(row):
            return Messagelte(
                        frame_number=row['frame.number'],
                        frame_time=row['frame.time'],
                        ip_src=row['ip.src'],
                        ip_dst=row['ip.dst'],
                        protocol=row['frame.protocols'],
                        message=row['_ws.col.info'],
                        src_node=row['srcNode'],
                        dst_node=row['dstNode'],
                        message_json=None,
                        c_rnti=row['mavlterrc.rnti'],
                        enb_ue_s1ap_id=row['s1ap.ENB_UE_S1AP_ID'],
                        mme_ue_s1ap_id=row['s1ap.MME_UE_S1AP_ID'],
                        x2ap_ue_ran_id=row['x2ap.UE_X2AP_ID'],
                        x2ap_5g_ran_id=row['x2ap.SgNB_UE_X2AP_ID'],
                        uploaded_file_id=item_id,
                        gnb_id=np.nan,
                        identifiers_id=identifier_data.id,
                        s1ap_cause=row.get('s1ap.cause_desc', None),
                        nas_cause=row.get('nas.cause_desc', None),
                        x2ap_cause=row.get('x2ap.cause_desc', None)
            )

        try:
            messages = updated_messages.apply(create_message, axis=1)
        except Exception as e:
            logging.error(f"An error occurred in create_message_instances: {str(e)}")

        return messages.tolist()


    @classmethod
    def create_bulk_update_data(cls, updated_messages, identifier_data):
        try:
            rrc_stats = sh.calculate_rrc_stats(updated_messages)
            initial_ctxt_stats = sh.calculate_initial_ctxt_stats(updated_messages)
            pdn_ctxt_stats = sh.calculate_pdn_stats(updated_messages)
            x2ap_handover_stats = sh.calculate_x2ap_handover_stats(updated_messages)
            s1ap_handover_stats = sh.calculate_s1ap_handover_stats(updated_messages)
            x2ap_sgNBadd_stats = sh.calculate_x2ap_sgNBadd_stats(updated_messages)

            #cause_code = sh.get_cause_data(updated_messages)
            bulk_update_data = {
                'id': identifier_data.id,
                **rrc_stats,
                **initial_ctxt_stats,
                **pdn_ctxt_stats,
                **x2ap_handover_stats,
                **s1ap_handover_stats,
                **x2ap_sgNBadd_stats,
              #  **cause_code,
            }
        except Exception as e:
            logging.error(f"An error occurred in processing stats: {str(e)}")
            return None
        return bulk_update_data

    @classmethod
    def bulk_update_identifiers(cls, bulk_update_data):
        logging.error(f"Identifier update with Stats Started. {len(bulk_update_data)}")

        for data in bulk_update_data:
            identifier_id = data['id']
            Identifierslte.objects.update_or_create(
                id=identifier_id,
                defaults=data,
            )
        logging.error(f"Identifier update has been completed!!")
