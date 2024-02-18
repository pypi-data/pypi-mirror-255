from datetime import timedelta
from drawranflow.models import Identifierslte
import logging
from django.utils import timezone


class computeStats:
    def __init__(self):
        pass

    @classmethod
    def packet_to_json(cls, packet):
        # Extract IP layer if it exists
        new_dict = {}
        for key in packet:
            # split the key by the first dot and get the top-level key and the second-level key suffix
            if key != "" and "per" not in key:
                if "." in key:
                    top_level_key, suffix = key.split(".", 1)
                else:
                    top_level_key = key
                    suffix = ""

                # create a new dictionary with the top-level key if it doesn't exist
                if top_level_key not in new_dict:
                    new_dict[top_level_key] = {}

                    # add the second-level key suffix and its value to the new dictionary
                new_dict[top_level_key][suffix] = packet[key]
        return new_dict

    @classmethod
    def packetLayers(cls, packet):

        ipadd = packet.ip._all_fields if 'IP' in packet else {}
        s1ap = packet.s1ap._all_fields if 'S1AP' in packet else {}
        mvlterrc = packet.MAVLTERRC._all_fields if 'MAVLTERRC' in packet else {}
        x2ap = packet.x2ap._all_fields if 'X2AP' in packet else {}

        filtered_ipdata = {key: value for key, value in ipadd.items() if key in ["ip.src", "ip.dst"]}
        del packet
        return {**filtered_ipdata, **s1ap, **mvlterrc, **x2ap}

    @classmethod
    def calculate_rrc_stats(cls, updated_messages):
        logging.debug("calculate_rrc_stats - Started.")
        time_window = timezone.timedelta(seconds=1)
        rrc_setup_success = 0
        # Extract counts for each RRC-related message type
        rrc_setup_attempts = len(updated_messages[
                                     (updated_messages['_ws.col.info'] == 'RRCConnectionSetup') &
                                     (updated_messages['frame.protocols'].str.contains('lte_rrc', case=False, na=False))
                                     ])

        if rrc_setup_attempts > 0:
            rrc_setup_messages = updated_messages[
                (updated_messages['_ws.col.info'] == 'RRCConnectionSetup') &
                (updated_messages['frame.protocols'].str.contains('lte_rrc', case=False, na=False))
                ].copy()  # Add .copy() to create a copy of the slice

            one_second = timedelta(seconds=1)

            rrc_setup_messages.loc[:, 'start_time'] = rrc_setup_messages['frame.time']
            rrc_setup_messages.loc[:, 'end_time'] = rrc_setup_messages['frame.time'] + one_second

            # Check if any of the specified messages occur within the time window of each 'RRC Setup'
            specified_messages_within_one_second = updated_messages[
                ((updated_messages['_ws.col.info'] == 'RRCConnectionSetupComplete') |
                 (updated_messages['_ws.col.info'] == 'Registration request') |
                 (updated_messages['_ws.col.info'] == 'Tracking area update request') |
                 (updated_messages['_ws.col.info'] == 'Service request') |
                 (updated_messages['_ws.col.info'].str.contains('PDN conn',case=False, na=False))) &
                (updated_messages['frame.protocols'].str.contains('lte', case=False, na=False)) &
                updated_messages['frame.time'].between(rrc_setup_messages['start_time'].min(),
                                                       rrc_setup_messages['end_time'].max())
                ].copy()  # Add .copy() to create a copy of the slice

            rrc_setup_success = min(len(specified_messages_within_one_second), 1)

        rrc_setup_failure = min(len(updated_messages[
                                        (updated_messages['_ws.col.info'] == 'RRCConnectionReject') &
                                        (updated_messages['frame.protocols'].str.contains('lte', case=False, na=False))
                                        ]), 1)

        rrc_setup_timeout = 1 if (
                rrc_setup_attempts > 0 and
                rrc_setup_success == 0 and
                rrc_setup_failure == 0
        ) else 0

        logging.debug("calculate_rrc_stats - Completed.")
        return {
            'rrc_setup_attempts': rrc_setup_attempts,
            'rrc_setup_success': rrc_setup_success,
            'rrc_setup_failure': rrc_setup_failure,
            'rrc_setup_timeout': rrc_setup_timeout,
        }

    @classmethod
    def calculate_initial_ctxt_stats(cls, updated_messages):
        logging.debug("calculate_initial_ctxt_stats - Started.")
        filtered_messages = updated_messages[updated_messages['frame.protocols'].str.contains('s1ap', case=False, na=False)]
        updated_messages = filtered_messages.copy()
        # Extract counts for each initial context-related message type
        msg_to_check = ['Registration request','Service request','Tracking area update request','PDN connectivity request']
        initial_ctxt_setup_request =0
        for i in range(len(updated_messages) - 1):
            if any(msg in updated_messages.iloc[i]['_ws.col.info'] for msg in msg_to_check):

                if ('UECapability' in updated_messages.iloc[i + 1]['_ws.col.info'] or
                        'InitialContext' in updated_messages.iloc[i + 1]['_ws.col.info'] or
                        'Activate default' in updated_messages.iloc[i + 1]['_ws.col.info'] or
                        updated_messages['_ws.col.info'].astype(str).str.contains("InitialContext").any()):
                    initial_ctxt_setup_request =1

        initial_ctxt_setup_response = len(updated_messages[
                                              (updated_messages['_ws.col.info'] == 'InitialContextSetupResponse') &
                                              (updated_messages['frame.protocols'].str.contains('s1ap', case=False,
                                                                                                na=False))
                                              ])

        initial_ctxt_setup_failure = len(updated_messages[
                                             (updated_messages['_ws.col.info'] == 'InitialContextSetupFailure') &
                                             (updated_messages['frame.protocols'].str.contains('s1ap', case=False,
                                                                                               na=False))
                                             ])

        # Check for timeouts
        initial_ctxt_timeout = 1 if (
                initial_ctxt_setup_request > 0 and
                initial_ctxt_setup_response == 0 and
                initial_ctxt_setup_failure == 0
        ) else 0

        logging.debug("calculate_initial_ctxt_stats - Completed.")

        return {
            'initial_ctxt_attempts': initial_ctxt_setup_request,
            'initial_ctxt_success': initial_ctxt_setup_response,
            'initial_ctxt_failure': initial_ctxt_setup_failure,
            'initial_ctxt_timeout': initial_ctxt_timeout,
        }

    @classmethod
    def calculate_pdn_stats(cls, updated_messages):

        logging.debug("calculate_bearerctxt_stats - Started.")
        # Extract counts for each bearer context-related message type
        bearerctxt_setup_request = len(updated_messages[
                                           (updated_messages['_ws.col.info'] == 'PDN connectivity request') &
                                           (updated_messages['frame.protocols'].str.contains('s1ap', case=False,
                                                                                             na=False))
                                           ])

        bearerctxt_setup_response = len(updated_messages[
                                            (updated_messages['_ws.col.info'] == 'PDN connectivity response') &
                                            (updated_messages['frame.protocols'].str.contains('s1ap', case=False,
                                                                                              na=False))
                                            ])

        bearerctxt_setup_failure = len(updated_messages[
                                           (updated_messages['_ws.col.info'] == 'PDN connectivity reject') &
                                           (updated_messages['frame.protocols'].str.contains('s1ap', case=False,
                                                                                             na=False))
                                           ])

        # Check for timeouts
        bearerctxt_timeout = 1 if (
                bearerctxt_setup_request > 0 and
                bearerctxt_setup_response == 0 and
                bearerctxt_setup_failure == 0
        ) else 0

        logging.debug("pdn_conn_stats - Completed.")

        return {
            'pdn_conn_attempts': bearerctxt_setup_request,
            'pdn_conn_success': bearerctxt_setup_response,
            'pdn_conn_failure': bearerctxt_setup_failure,
            'pdn_conn_timeout': bearerctxt_timeout,
        }


    @classmethod
    def calculate_s1ap_handover_stats(cls, updated_messages):
        logging.debug("calculate_s1ap_handover_stats - Started.")

        # Extract counts for each handover-related message type
        xnap_handover_request_attempts = len(updated_messages[
                                                 (updated_messages['_ws.col.info'] == 'HandoverRequest') &
                                                 (updated_messages['frame.protocols'].str.contains('s1ap', case=False,
                                                                                                   na=False))
                                                 ])

        xnap_handover_request_ack_success = len(updated_messages[
                                                    (updated_messages['_ws.col.info'] == 'HandoverRequestAcknowledge') &
                                                    (updated_messages['frame.protocols'].str.contains('s1ap',
                                                                                                      case=False,
                                                                                                      na=False))
                                                    ])

        xnap_handover_failure = len(updated_messages[
                                        (updated_messages['_ws.col.info'] == 'HandoverFailure') & (
                                                updated_messages['_ws.col.info'] == 'HandoverCancel') &
                                        (updated_messages['frame.protocols'].str.contains('s1ap', case=False, na=False))
                                        ])

        xnap_handover_timeout = 1 if (
                xnap_handover_request_attempts > 0 and
                xnap_handover_request_ack_success == 0 and
                xnap_handover_failure == 0
        ) else 0

        logging.debug("calculate_s1ap_handover_stats - Completed.")

        return {
            's1ap_ho_attempts': xnap_handover_request_attempts,
            's1ap_ho_success': xnap_handover_request_ack_success,
            's1ap_ho_failure': xnap_handover_failure,
            's1ap_ho_timeout': xnap_handover_timeout,
        }

    @classmethod
    def calculate_x2ap_handover_stats(cls, updated_messages):
        logging.debug("calculate_s1ap_handover_stats - Started.")

        # Extract counts for each handover-related message type
        xnap_handover_request_attempts = len(updated_messages[
                                                 (updated_messages['_ws.col.info'] == 'HandoverRequest') &
                                                 (updated_messages['frame.protocols'].str.contains('s1ap', case=False,
                                                                                                   na=False))
                                                 ])

        xnap_handover_request_ack_success = len(updated_messages[
                                                    (updated_messages['_ws.col.info'] == 'HandoverRequestAcknowledge') &
                                                    (updated_messages['frame.protocols'].str.contains('s1ap',
                                                                                                      case=False,
                                                                                                      na=False))
                                                    ])

        xnap_handover_failure = len(updated_messages[
                                        (updated_messages['_ws.col.info'] == 'HandoverFailure') & (
                                                updated_messages['_ws.col.info'] == 'HandoverCancel') &
                                        (updated_messages['frame.protocols'].str.contains('s1ap', case=False, na=False))
                                        ])

        xnap_handover_timeout = 1 if (
                xnap_handover_request_attempts > 0 and
                xnap_handover_request_ack_success == 0 and
                xnap_handover_failure == 0
        ) else 0

        logging.debug("calculate_s1ap_handover_stats - Completed.")

        return {
            'x2ap_ho_attempts': xnap_handover_request_attempts,
            'x2ap_ho_success': xnap_handover_request_ack_success,
            'x2ap_ho_failure': xnap_handover_failure,
            'x2ap_ho_timeout': xnap_handover_timeout,
        }

    @classmethod
    def calculate_x2ap_sgNBadd_stats(cls, updated_messages):
        logging.debug("calculate_s1ap_handover_stats - Started.")

        # Extract counts for each handover-related message type
        xnap_handover_request_attempts = len(updated_messages[
                                                 (updated_messages['_ws.col.info'] == 'SgNBAdditionRequest') &
                                                 (updated_messages['frame.protocols'].str.contains('x2ap', case=False,
                                                                                                   na=False))
                                                 ])

        xnap_handover_request_ack_success = len(updated_messages[(
                                                    (updated_messages['_ws.col.info'] == 'SgNBAdditionRequestAcknowledge') |
                                                    (updated_messages['_ws.col.info'] == 'RRC Reconfiguration')) &
                                                    (updated_messages['frame.protocols'].str.contains('x2ap',
                                                                                                      case=False,
                                                                                                      na=False))
                                                    ])

        xnap_handover_failure = len(updated_messages[
                                        (updated_messages['_ws.col.info'] == 'SgNBAdditionRequestFailure') & (
                                                updated_messages['_ws.col.info'] == 'SgNBAdditionRequestReject') &
                                        (updated_messages['frame.protocols'].str.contains('x2ap', case=False, na=False))
                                        ])

        xnap_handover_timeout = 1 if (
                xnap_handover_request_attempts > 0 and
                xnap_handover_request_ack_success == 0 and
                xnap_handover_failure == 0
        ) else 0

        logging.debug("calculate_s1ap_handover_stats - Completed.")

        return {
            'x2ap_sgNBadd_attempts': xnap_handover_request_attempts,
            'x2ap_sgNBadd_success': xnap_handover_request_ack_success,
            'x2ap_sgNBadd_failure': xnap_handover_failure,
            'x2ap_sgNBadd_timeout': xnap_handover_timeout,
        }

    @classmethod
    def get_gnb_ids(cls, file_id):
        unique_gnb_ids_with_ips = Identifierslte.objects.filter(
            uploaded_file_id=file_id,
            gnb_id__isnull=False,
        ).exclude(gnb_id="").values('gnb_id', 'cucp_f1c_ip').order_by('gnb_id').distinct()
        formatted_results = [f"{pair['gnb_id']}({pair['cucp_f1c_ip']})" for pair in unique_gnb_ids_with_ips]

        return formatted_results

    @classmethod
    def get_cause_data(cls, updated_messages):
        s1ap_cause = next(iter(updated_messages['s1ap.cause_desc'].dropna()), None)
        x2ap_cause = next(iter(updated_messages['x2ap.cause_desc'].dropna()), None)
        nas_cause = next(iter(updated_messages['nas.cause_desc'].dropna()), None)
        return {
            's1ap_cause': s1ap_cause,
            'x2ap_cause': x2ap_cause,
            'nas_cause': nas_cause,
        }
