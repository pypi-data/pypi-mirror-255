import logging
import os
import subprocess
import platform
import pandas as pd
from drawranflow.servicelogic.handlers import message_handler_sa as fh
from drawranflow.models import UploadedFile
from django.utils import timezone
from django.conf import settings
import numpy as np
from .utils_sa import load_cause_config
from .files_handler_sa import FileHandlers
import shutil

current_os = platform.system()
BASE_DIR = getattr(settings, 'BASE_DIR', None)


def extract_last_info(row):
    global part
    if "Not used in current version" in row:
        parts = row.split(', Not')[0]
        row = parts
    elif " (" in row:
        parts = row.split(' (')[0]
        row = parts
    elif '[Mal' in row or '[Bound' in row:
        parts = row.split('[')[0]
        row = parts
    parts = row.split(', ')
    for part in reversed(parts):
        if 'MAC=' in part:
            return part.split('MAC=')[0].rstrip()
        if '[' in part:
            return part.split('[')[0].strip()
        if '(' in part and "SACK (Ack=" not in part:
            return part.split('(')[0].strip()
        return part.rstrip()


def split_values(row):
    value = str(row['xnap.NG_RANnodeUEXnAPID'])
    value = value.strip()
    if pd.notna(value) and value.lower() != 'nan':
        values = value.split(',')
        return pd.Series([values[0] if len(values) > 0 else np.nan, values[1] if len(values) > 1 else np.nan])
    else:
        return pd.Series([np.nan, np.nan])


class packetHandler:
    def __init__(self, input_pcap, output_csv, item_id):
        self.input_pcap = input_pcap
        self.output_csv = output_csv
        self.item_id = item_id

    def fix_pcap(self):
        output = subprocess.check_output(["pcapfix", "-d", self.input_pcap])
        if "SUCCESS" in output.decode():
            logging.error("Fixed pcap `cut short in the middle of a packet in deep mode` issue and processing...")
            dir, filename = os.path.split(self.input_pcap)
            fixed_path = f'{BASE_DIR}/fixed_{filename}'
            shutil.move(fixed_path, self.input_pcap)
            # self.input_pcap = f"fixed_{self.input_pcap}"
        else:
            output = subprocess.check_output(["pcapfix", "-s", self.input_pcap])
            if "SUCCESS" in output.decode():
               logging.error("Fixed pcap `cut short in the middle of a packet in soft mode` issue and processing...")
               dir, filename = os.path.split(self.input_pcap)
               fixed_path = f'{BASE_DIR}/fixed_{filename}'
               shutil.move(fixed_path, self.input_pcap)


    def capture_packets_and_save_to_csv(self):
        logging.error("Filtering required protocols")
        try:

            filtered_file = f'{self.input_pcap}_filtered'

            tshark_c = ['tshark', '-r', self.input_pcap, '-Y', 'f1ap||e1ap||ngap||xnap||s1ap', '-w', filtered_file]
            try:
                # Define the tshark command
                result = subprocess.run(tshark_c, stdout=subprocess.PIPE, text=True, check=True)
            except subprocess.CalledProcessError as e:
                logging.error(f"subprocess.run() failed with return code {e.returncode}")
                if e.returncode == 2:
                    logging.error("The process exited with return code 2")
                    self.fix_pcap()
                    result = subprocess.run(tshark_c, stdout=subprocess.PIPE, text=True, check=True)
                    pass
            os.replace(filtered_file, self.input_pcap)

            if result:
                if current_os == "Windows" or current_os == "Linux":
                    logging.error(f"Detected OS is {current_os}")

                    tshark_command = [
                        'tshark', '-r', self.input_pcap, '-T', 'fields',
                        '-e', 'frame.number',
                        '-e', 'frame.time',
                        '-e', 'ip.src',
                        '-e', 'ip.dst',
                        '-e', 'frame.protocols',
                        '-e', 'f1ap.C_RNTI',
                        '-e', 'f1ap.GNB_DU_UE_F1AP_ID',
                        '-e', 'f1ap.GNB_CU_UE_F1AP_ID',
                        '-e', 'f1ap.nRCellIdentity',
                        '-e', 'e1ap.GNB_CU_CP_UE_E1AP_ID',
                        '-e', 'e1ap.GNB_CU_UP_UE_E1AP_ID',
                        '-e', 'ngap.RAN_UE_NGAP_ID',
                        '-e', 'ngap.AMF_UE_NGAP_ID',
                        '-e', 'f1ap.procedureCode',
                        '-e', 'e1ap.procedureCode',
                        '-e', 'ngap.procedureCode',
                        '-e', 'f1ap.pLMN_Identity',
                        '-e', 'nr-rrc.ng_5G_S_TMSI_Part1',
                        '-e', 'nr-rrc.pdcch_DMRS_ScramblingID',
                        '-e', 'nas_5gs.sm.message_type',
                        '-e', 'nas_5gs.mm.message_type',
                        '-e', '_ws.col.Info',
                        '-e', 'xnap.NG_RANnodeUEXnAPID',
                        '-e', 'xnap.NR_Cell_Identity',
                        '-e', 'ngap.NRCellIdentity',
                        '-e', 'f1ap.transport',
                        '-e', 'f1ap.protocol',
                        '-e', 'f1ap.misc',
                        '-e', 'f1ap.radioNetwork',
                        '-e', 'ngap.transport',
                        '-e', 'ngap.protocol',
                        '-e', 'ngap.misc',
                        '-e', 'ngap.radioNetwork',
                        '-e', 'ngap.nas',
                        '-e', 'nas_5gs.sm.5gsm_cause',
                        '-e', 'nas_5gs.mm.5gmm_cause',
                        '-e', 'nr-rrc.c_RNTI',
                        '-e','nr-rrc.reestablishmentCause',
                        '-E', 'header=y',
                        '-E', 'separator=;',
                        '-Y', 'f1ap||e1ap||ngap||xnap'
                    ]

                if current_os == "Darwin":  # macOS

                    logging.error(f"Detected OS is {current_os}")

                    tshark_command = [
                        'tshark', '-r', self.input_pcap, '-T', 'fields',
                        '-e', 'frame.number',
                        '-e', 'frame.time',
                        '-e', 'ip.src',
                        '-e', 'ip.dst',
                        '-e', 'frame.protocols',
                        '-e', 'f1ap.C_RNTI',
                        '-e', 'f1ap.GNB_DU_UE_F1AP_ID',
                        '-e', 'f1ap.GNB_CU_UE_F1AP_ID',
                        '-e', 'f1ap.nRCellIdentity',
                        '-e', 'e1ap.GNB_CU_CP_UE_E1AP_ID',
                        '-e', 'e1ap.GNB_CU_UP_UE_E1AP_ID',
                        '-e', 'ngap.RAN_UE_NGAP_ID',
                        '-e', 'ngap.AMF_UE_NGAP_ID',
                        '-e', 'f1ap.procedureCode',
                        '-e', 'e1ap.procedureCode',
                        '-e', 'ngap.procedureCode',
                        '-e', 'f1ap.pLMN_Identity',
                        '-e', 'nr-rrc.ng_5G_S_TMSI_Part1',
                        '-e', 'nr-rrc.pdcch_DMRS_ScramblingID',
                        '-e', 'nas_5gs.sm.message_type',
                        '-e', 'nas_5gs.mm.message_type',
                        '-e', 'f1ap.transport',
                        '-e', 'f1ap.protocol',
                        '-e', 'f1ap.misc',
                        '-e', 'f1ap.radioNetwork',
                        '-e', 'ngap.transport',
                        '-e', 'ngap.protocol',
                        '-e', 'ngap.misc',
                        '-e', 'ngap.radioNetwork',
                        '-e', 'ngap.nas',
                        '-e', '_ws.col.Info',
                        '-e', 'xnap.NG_RANnodeUEXnAPID',
                        '-e', 'xnap.NR_Cell_Identity',
                        '-e', 'ngap.NRCellIdentity',
                        '-e', 'nas_5gs.sm.5gsm_cause',
                        '-e', 'nas_5gs.mm.5gmm_cause',
                        '-e', 'nr-rrc.c_RNTI',
                        '-e', 'nr-rrc.reestablishmentCause',
                        '-E', 'header=y',
                        '-E', 'separator=;',
                        '-Y', 'f1ap||e1ap||ngap||xnap'
                    ]
                try:
                    # Run tshark and capture the output
                    result = subprocess.run(tshark_command, stdout=subprocess.PIPE, text=True, check=True)

                except subprocess.CalledProcessError as e:
                    logging.error(f"subprocess.run() failed with return code {e.returncode}")
                    if e.returncode == 2:
                        logging.error("The process exited with return code 2")
                        self.file_prefix
                        result = subprocess.run(tshark_command, stdout=subprocess.PIPE, text=True, check=True)
                        pass
                # Save the CSV data to the output file
                with open(self.output_csv, 'w') as csv_file:
                    csv_created = csv_file.write(result.stdout)
                upload_file = UploadedFile.objects.get(id=self.item_id)
                # logging.debug(f"Tshark successfully filterd and csv created , {result}, {csv_created}")

                if result and csv_created:
                    # setattr(upload_file, 'processDate', timezone.now())
                    # setattr(upload_file, 'processed', True)
                    pass
                upload_file.save()
                logging.error(f"Exported tshark data to {self.output_csv}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error running tshark: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        if current_os == "Darwin":
            logging.error(f"Calling Mac OS function")

            dtypes = {
                'frame.number': str,
                'frame.time': str,
                'ip.src': str,
                'ip.dst': str,
                'frame.protocols': str,
                'f1ap.C_RNTI': str,
                'f1ap.GNB_DU_UE_F1AP_ID': str,
                'f1ap.GNB_CU_UE_F1AP_ID': str,
                'f1ap.nRCellIdentity': str,
                'e1ap.GNB_CU_CP_UE_E1AP_ID': str,
                'e1ap.GNB_CU_UP_UE_E1AP_ID': str,
                'ngap.RAN_UE_NGAP_ID': str,
                'ngap.AMF_UE_NGAP_ID': str,
                'f1ap.procedureCode': str,
                'e1ap.procedureCode': str,
                'ngap.procedureCode': str,
                'f1ap.pLMN_Identity': str,
                'nr-rrc.ng_5G_S_TMSI_Part1': str,
                'nr-rrc.pdcch_DMRS_ScramblingID': str,
                'nas_5gs.sm.message_type': str,
                'nas_5gs.mm.message_type': str,
                '_ws.col.Info': str,
                'xnap.NG_RANnodeUEXnAPID': str,
                'xnap.NR_Cell_Identity': str,
                'ngap.NRCellIdentity': str,
                'f1ap.transport': str,
                'f1ap.protocol': str,
                'f1ap.misc': str,
                'f1ap.radioNetwork': str,
                'ngap.transport': str,
                'ngap.protocol': str,
                'ngap.misc': str,
                'ngap.radioNetwork': str,
                'ngap.nas': str,
                'nr-rrc.reestablishmentCause': str,
                'nr-rrc.c_RNTI': str,
                'nas-5gs.mm.5gmm_cause': str,
                'nas-5gs.sm.5gsm_cause': str,
            }
            df = pd.read_csv(self.output_csv, sep=';', dtype=dtypes, parse_dates=['frame.time'])
            df.loc[:, '_ws.col.info'] = df['_ws.col.info'].apply(extract_last_info)
            df = df.rename(columns={"nas_5gs.sm.message_type": "nas-5gs.sm.message_type",
                                    "nas_5gs.mm.message_type": "nas-5gs.mm.message_type",
                                    "nas-5gs.mm.5gmm_cause": "nas_5gs.mm.5gmm_cause",
                                    })
            df[['xnap.NG_RANnodeUEXnAPID_src', 'xnap.NG_RANnodeUEXnAPID_dst']] = df.apply(split_values, axis=1)

            # Drop the original 'NG_RANnodeUEXnAPID and _ws.col.Info' column
            df = df.drop('xnap.NG_RANnodeUEXnAPID', axis=1)

        if current_os == 'Windows' or current_os == 'Linux':
            logging.error(f"Detected OS is Linux/WSL")

            dtypes = {
                'frame.number': str,
                'frame.time': str,
                'ip.src': str,
                'ip.dst': str,
                'frame.protocols': str,
                'f1ap.C_RNTI': str,
                'f1ap.GNB_DU_UE_F1AP_ID': str,
                'f1ap.GNB_CU_UE_F1AP_ID': str,
                'f1ap.nRCellIdentity': str,
                'e1ap.GNB_CU_CP_UE_E1AP_ID': str,
                'e1ap.GNB_CU_UP_UE_E1AP_ID': str,
                'ngap.RAN_UE_NGAP_ID': str,
                'ngap.AMF_UE_NGAP_ID': str,
                'f1ap.procedureCode': str,
                'e1ap.procedureCode': str,
                'ngap.procedureCode': str,
                'f1ap.pLMN_Identity': str,
                'nr-rrc.ng_5G_S_TMSI_Part1': str,
                'nr-rrc.pdcch_DMRS_ScramblingID': str,
                'nas-5gs.sm.message_type': str,
                'nas-5gs.mm.message_type': str,
                '_ws.col.Info': str,
                'xnap.NG_RANnodeUEXnAPID': str,
                'xnap.NR_Cell_Identity': str,
                'ngap.NRCellIdentity': str,
                'f1ap.transport': str,
                'f1ap.protocol': str,
                'f1ap.misc': str,
                'f1ap.radioNetwork': str,
                'ngap.transport': str,
                'ngap.protocol': str,
                'ngap.misc': str,
                'ngap.radioNetwork': str,
                'ngap.nas': str,
                'nas_5gs.mm.5gmm_cause': str,
                'nas_5gs.sm.5gsm_cause': str,
                'nr-rrc.reestablishmentCause': str,
                'nr-rrc.c_RNTI': str
            }
            logging.error("Loading csv to pd Data Frame")
            df = pd.read_csv(self.output_csv, sep=';', dtype=dtypes, parse_dates=['frame.time'])
            logging.error("Loading csv to pd Data Frame Completed!!")

            logging.error("Scrubbing or Manipulating messages")
            df['_ws.col.info'] = df['_ws.col.Info'].apply(extract_last_info)
            # Rename columns
            logging.error("Scrubbing or Manipulating messages completed!!")
            df = df.rename(columns={"nas_5gs.sm.message_type": "nas-5gs.sm.message_type",
                                    "nas_5gs.mm.message_type": "nas-5gs.mm.message_type",
                                    "nr-rrc.pdcch_DMRS_ScramblingID": "nr-rrc.pdcch_DMRS_ScramblingID"})

            logging.error("Identifying xnap src and dst transactions..")

            #df[['xnap.NG_RANnodeUEXnAPID_src', 'xnap.NG_RANnodeUEXnAPID_dst']] = df.apply(split_values, axis=1)
            df['xnap.NG_RANnodeUEXnAPID_src'] = df['xnap.NG_RANnodeUEXnAPID'].str.split(',').str[0]
            df['xnap.NG_RANnodeUEXnAPID_dst'] = df['xnap.NG_RANnodeUEXnAPID'].str.split(',').str[1]
            df['f1ap.GNB_DU_UE_F1AP_ID_org'] = df['f1ap.GNB_DU_UE_F1AP_ID'].str.split(',').str[0]
            df['f1ap.GNB_DU_UE_F1AP_ID_ho'] = df['f1ap.GNB_DU_UE_F1AP_ID'].str.split(',').str[1]
            df['f1ap.GNB_DU_UE_F1AP_ID'] = df['f1ap.GNB_DU_UE_F1AP_ID_org']
            logging.error("Identifying xnap src and dst transactions completed!!")

            # Drop the original 'NG_RANnodeUEXnAPID and _ws.col.Info' column
            df = df.drop(['_ws.col.Info', 'xnap.NG_RANnodeUEXnAPID'], axis=1)

        # Mapping F1AP Cause Code
        logging.error(f"Started F1 cos code mapping process")
        f1ap_cause_df = load_cause_config("f1ap")

        for f1col in f1ap_cause_df.columns:
            mask = pd.notna(df[f1col])
            # Map descriptions only for non-NaN values
            df.loc[mask, "f1ap.cause_desc"] = df.loc[mask, f1col].map(f1ap_cause_df[f1col])
        logging.error(f"f1ap cos codes mapping completed")

        # Mapping NGAP Cause Code
        logging.error(f"Started ngap cos code mapping process")
        ngap_cause_df = load_cause_config("ngap")

        for ngcol in ngap_cause_df.columns:
            mask = pd.notna(df[ngcol])
            # Map descriptions only for non-NaN values
            df.loc[mask, "ngap.cause_desc"] = df.loc[mask, ngcol].map(ngap_cause_df[ngcol])

        logging.error(f"Ngap codes mapping completed")

        # Mapping NAS Cause Code
        logging.error(f"Started nas cos code mapping process")
        nas_cause_df = load_cause_config("nas")
        for nascol in nas_cause_df.columns:
            mask = pd.notna(df[nascol])
            # Map descriptions only for non-NaN values
            df.loc[mask, "nas.cause_desc"] = df.loc[mask, nascol].map(nas_cause_df[nascol])
        logging.error(f"nas codes mapping completed")
        rrc_cause_df = load_cause_config("rrc")

        for rrccol in rrc_cause_df.columns:
            mask = pd.notna(df[rrccol])
            # Map descriptions only for non-NaN values
            df.loc[mask, "rre.cause_desc"] = df.loc[mask, rrccol].map(rrc_cause_df[rrccol])

        logging.error(f"RRE codes mapping completed")
        print(df['rre.cause_desc'])
        fh.message_handler(df, self.item_id)
        fh.update_messages_with_identifier_key(df, self.item_id)
