import logging
import os
import subprocess
import platform
import pandas as pd
from drawranflow.servicelogic.handlers import message_handler_lte as mh
from drawranflow.models import UploadedFile
from django.utils import timezone
from django.conf import settings
import numpy as np
from .utils_sa import load_cause_config
from .files_handler_lte import FileHandlers
import shutil

current_os = platform.system()
BASE_DIR = getattr(settings, 'BASE_DIR', None)


def extract_last_info(row):
    global parts
    if 'UECapabilityInformation' in row: 
        parts = row.split(',')
        if len(parts) > 1 and "Len" not in parts[0]:
            row = parts[0]
    elif "Ciphered" in row:
        parts = row.split(', Ciphered')[0]
        row = parts
    elif "Not used in current version" in row:
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
            logging.error("Fixed pcap `cut short in the middle of a packet` issue and processing...")
            dir, filename = os.path.split(self.input_pcap)
            fixed_path = f'{BASE_DIR}/fixed_{filename}'
            shutil.move(fixed_path, self.input_pcap)
                    # self.input_pcap = f"fixed_{self.input_pcap}"

    def capture_packets_and_save_to_csv(self):
        global upload_file, tshark_command, df
        logging.error("Filtering required protocols")
        try:
            result = None
            filtered_file = f'{self.input_pcap}_filtered'
            
            tshark_c = ['tshark', '-r', self.input_pcap, '-Y', 's1ap||x2ap||lte_rrc', '-w', filtered_file]
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
                    logging.error(f"Detected OS is Linux")

                    tshark_command = [
                        'tshark', '-r', self.input_pcap, '-T', 'fields',
                        '-e', 'frame.number',
                        '-e', 'frame.time',
                        '-e', 'ip.src',
                        '-e', 'ip.dst',
                        '-e', 'frame.protocols',
                        '-e', 'nas_5gs.sm.message_type',
                        '-e', 'nas_5gs.mm.message_type',
                        '-e', '_ws.col.Info',
                        '-e', 'nas_5gs.sm.5gsm_cause',
                        '-e', 'nas_5gs.mm.5gmm_cause',
                        '-e', 'nas_eps.emm.m_tmsi',
                        '-e', 'mavlterrc.rnti',
                        '-e', 'mavlterrc.cellid',
                        '-e', 's1ap.ENB_UE_S1AP_ID',
                        '-e', 's1ap.MME_UE_S1AP_ID',
                        '-e', 's1ap.CellIdentity',
                        '-e', 'x2ap.eUTRANcellIdentifier',
                        '-e', 'e212.imsi',
                        '-e', 'x2ap.UE_X2AP_ID',
                        '-e', 'x2ap.SgNB_UE_X2AP_ID',
                        '-e', 's1ap.pLMN_Identity',
                        '-e', 'x2ap.gTP_TEID',
                        '-e', 's1ap.gTP_TEID',
                        '-E', 'header=y',
                        '-E', 'separator=;',
                        '-Y', 's1ap||x2ap||lte_rrc'
                    ]

                if current_os == "Darwin":  # macOS

                    logging.error(f"Detected OS is Mac")
                    tshark_command = [
                        'tshark', '-r', self.input_pcap, '-T', 'fields',
                        '-e', 'frame.number',
                        '-e', 'frame.time',
                        '-e', 'ip.src',
                        '-e', 'ip.dst',
                        '-e', 'frame.protocols',
                        '-e', 'nas_5gs.sm.message_type',
                        '-e', 'nas_5gs.mm.message_type',
                        '-e', '_ws.col.Info',
                        '-e', 'nas_5gs.sm.5gsm_cause',
                        '-e', 'nas_5gs.mm.5gmm_cause',
                        '-e', 'nas_eps.emm.m_tmsi',
                        '-e', 'mavlterrc.rnti',
                        '-e', 'mavlterrc.cellid',
                        '-e', 's1ap.ENB_UE_S1AP_ID',
                        '-e', 's1ap.MME_UE_S1AP_ID',
                        '-e', 's1ap.CellIdentity',
                        '-e', 'x2ap.eUTRANcellIdentifier',
                        '-e', 'e212.imsi',
                        '-e', 'x2ap.UE_X2AP_ID',
                        '-e', 'x2ap.SgNB_UE_X2AP_ID',
                        '-e', 's1ap.pLMN_Identity',
                        '-e', 'x2ap.gTP_TEID',
                        '-e', 's1ap.gTP_TEID',
                        '-E', 'header=y',
                        '-E', 'separator=;',
                        '-Y', 's1ap||x2ap||lte_rrc'
                    ]
                try:
                    result= None
                    # Run tshark and capture the output
                    result = subprocess.run(tshark_command, stdout=subprocess.PIPE, text=True, check=True)
                except subprocess.CalledProcessError as e:
                    logging.error(f"subprocess.run() failed with return code {e.returncode}")
                    
                    if e.returncode == 2:
                        logging.error("The process exited with return code 2")
                        self.fix_pcap()
                        result = subprocess.run(tshark_command, stdout=subprocess.PIPE, text=True, check=True)
                        pass
                # Save the CSV data to the output file
                with open(self.output_csv, 'w') as csv_file:
                    csv_created = csv_file.write(result.stdout)

                upload_file = UploadedFile.objects.get(id=self.item_id)
                logging.debug(f"Tshark successfully filterd and csv created , {result}, {csv_created}")
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
                'nas_5gs.sm.message_type': str,
                'nas_5gs.mm.message_type': str,
                '_ws.col.Info': str,
                'nas_5gs.mm.5gmm_cause': str,
                'nas_5gs.sm.5gsm_cause': str,
                'nas_eps.emm.m_tmsi': str,
                'mavlterrc.rnti': str,
                'mavlterrc.cellid': str,
                's1ap.ENB_UE_S1AP_ID': str,
                's1ap.MME_UE_S1AP_ID': str,
                'e212.imsi': str,
                's1ap.CellIdentity': str,
                'x2ap.eUTRANcellIdentifier': str,
                'x2ap.UE_X2AP_ID': str,
                'x2ap.SgNB_UE_X2AP_ID':str,
                's1ap.pLMN_Identity': str,
                'x2ap.gTP_TEID': str,
                's1ap.gTP_TEID': str,
            }
            df = pd.read_csv(self.output_csv, sep=';', dtype=dtypes, parse_dates=['frame.time'],low_memory=False)
            df = df[~df['_ws.col.Info'].str.contains("Port unreachable")]

            df['_ws.col.info'] = df['_ws.col.Info'].apply(extract_last_info)
            df = df[~df['_ws.col.Info'].str.contains("Port unreachable")]


        if current_os == 'Windows' or current_os == 'Linux':
            logging.error(f"Detected OS is Linux/WSL")
            dtypes = {
                'frame.number': str,
                'frame.time': str,
                'ip.src': str,
                'ip.dst': str,
                'frame.protocols': str,
                'nas_5gs.sm.message_type': str,
                'nas_5gs.mm.message_type': str,
                '_ws.col.Info': str,
                'nas_5gs.mm.5gmm_cause': str,
                'nas_5gs.sm.5gsm_cause': str,
                'nas_eps.emm.m_tmsi': str,
                'mavlterrc.rnti': str,
                'mavlterrc.cellid': str,
                's1ap.ENB_UE_S1AP_ID': str,
                's1ap.MME_UE_S1AP_ID': str,
                'e212.imsi': str,
                's1ap.CellIdentity': str,
                'x2ap.eUTRANcellIdentifier': str,
                'x2ap.UE_X2AP_ID': str,
                'x2ap.SgNB_UE_X2AP_ID':str,
                's1ap.pLMN_Identity': str,
                'x2ap.gTP_TEID': str,
                's1ap.gTP_TEID': str,
            }

            logging.error("Loading csv to pd Data Frame")
            df = pd.read_csv(self.output_csv, sep=';', dtype=dtypes, parse_dates=['frame.time'],encoding='utf-8')
            logging.error("Loading csv to pd Data Frame Completed!!")

            logging.error("Scrubbing or Manipulating messages")
            df['_ws.col.info'] = df['_ws.col.Info'].apply(extract_last_info)
            df = pd.read_csv(self.output_csv, sep=';', dtype=dtypes, parse_dates=['frame.time'],low_memory=False)
            df = df[~df['_ws.col.Info'].str.contains("Port unreachable")]

            df['_ws.col.info'] = df['_ws.col.Info'].apply(extract_last_info)
            df = df.rename(columns={"nas_5gs.sm.message_type": "nas-5gs.sm.message_type",
                                    "nas_5gs.mm.message_type": "nas-5gs.mm.message_type"})
            df['s1ap.ENB_UE_S1AP_ID'] = df['s1ap.ENB_UE_S1AP_ID'].str.split(',').str[0]
            df['s1ap.MME_UE_S1AP_ID'] = df['s1ap.MME_UE_S1AP_ID'].str.split(',').str[0]


            df = df.drop('_ws.col.Info', axis=1)
        mh.message_handler(df, self.item_id)

        mh.update_messages_with_identifier_key(df, self.item_id)
        setattr(upload_file, 'completeAt', timezone.now())
        setattr(upload_file, 'completed', True)
        upload_file.save()
        logging.error(f"Updated file as completed and set flag to TRUE")
