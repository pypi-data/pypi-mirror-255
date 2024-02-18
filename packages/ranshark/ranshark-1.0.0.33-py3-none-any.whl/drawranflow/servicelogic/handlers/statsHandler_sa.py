from datetime import timedelta
from drawranflow.models import Identifiers
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

        f1ap = packet.f1ap._all_fields if 'F1AP' in packet else {}
        e1ap = packet.e1ap._all_fields if 'E1AP' in packet else {}
        ngap = packet.ngap._all_fields if 'NGAP' in packet else {}
        xnap = packet.xnap._all_fields if 'XNAP' in packet else {}
        ipadd = packet.ip._all_fields if 'IP' in packet else {}
        s1ap = packet.s1ap._all_fields if 'S1AP' in packet else {}
        mvlterrc = packet.MAVLTERRC._all_fields if 'MAVLTERRC' in packet else {}
        x2ap = packet.x2ap._all_fields if 'X2AP' in packet else {}

        filtered_ipdata = {key: value for key, value in ipadd.items() if key in ["ip.src", "ip.dst"]}
        del packet
        return {**filtered_ipdata, **f1ap, **ngap, **e1ap, **xnap, **s1ap, **mvlterrc, **x2ap}

    @classmethod
    def calculate_rrc_stats(cls, updated_messages):
        logging.debug("calculate_rrc_stats - Started.")
        time_window = timezone.timedelta(seconds=1)
        rrc_setup_success = 0
        # Extract counts for each RRC-related message type
        rrc_setup_attempts = len(updated_messages[
                                     (updated_messages['_ws.col.info'] == 'RRC Setup') &
                                     (updated_messages['frame.protocols'].str.contains('f1ap', case=False, na=False))
                                     ])

        if rrc_setup_attempts > 0:
            rrc_setup_messages = updated_messages[
                (updated_messages['_ws.col.info'] == 'RRC Setup') &
                (updated_messages['frame.protocols'].str.contains('f1ap', case=False, na=False))
                ].copy()  # Add .copy() to create a copy of the slice

            one_second = timedelta(seconds=1)

            rrc_setup_messages.loc[:, 'start_time'] = rrc_setup_messages['frame.time']
            rrc_setup_messages.loc[:, 'end_time'] = rrc_setup_messages['frame.time'] + one_second

            # Check if any of the specified messages occur within the time window of each 'RRC Setup'
            specified_messages_within_one_second = updated_messages[
                ((updated_messages['_ws.col.info'] == 'RRC Setup Complete') |
                 (updated_messages['_ws.col.info'] == 'Registration request') |
                 (updated_messages['_ws.col.info'] == 'Tracking area update request') |
                 (updated_messages['_ws.col.info'] == 'Service request') |
                 (updated_messages['_ws.col.info'].str.contains('PDU Session'))) &
                (updated_messages['frame.protocols'].str.contains('f1ap', case=False, na=False)) &
                updated_messages['frame.time'].between(rrc_setup_messages['start_time'].min(),
                                                       rrc_setup_messages['end_time'].max())
                ].copy()  # Add .copy() to create a copy of the slice

            rrc_setup_success = min(len(specified_messages_within_one_second), 1)

        rrc_setup_failure = min(len(updated_messages[
                                        (updated_messages['_ws.col.info'] == 'RRC Reject') &
                                        (updated_messages['frame.protocols'].str.contains('f1ap', case=False, na=False))
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

        # Extract counts for each initial context-related message type
        initial_ctxt_setup_request = len(updated_messages[
                                             (updated_messages['_ws.col.info'] == 'InitialContextSetupRequest') &
                                             (updated_messages['frame.protocols'].str.contains('ngap', case=False,
                                                                                               na=False))
                                             ])

        initial_ctxt_setup_response = len(updated_messages[
                                              (updated_messages['_ws.col.info'] == 'InitialContextSetupResponse') &
                                              (updated_messages['frame.protocols'].str.contains('ngap', case=False,
                                                                                                na=False))
                                              ])

        initial_ctxt_setup_failure = len(updated_messages[
                                             (updated_messages['_ws.col.info'] == 'InitialContextSetupFailure') &
                                             (updated_messages['frame.protocols'].str.contains('ngap', case=False,
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
    def calculate_bearerctxt_stats(cls, updated_messages):

        logging.debug("calculate_bearerctxt_stats - Started.")
        # Extract counts for each bearer context-related message type
        bearerctxt_setup_request = len(updated_messages[
                                           (updated_messages['_ws.col.info'] == 'BearerContextSetupRequest') &
                                           (updated_messages['frame.protocols'].str.contains('e1ap', case=False,
                                                                                             na=False))
                                           ])

        bearerctxt_setup_response = len(updated_messages[
                                            (updated_messages['_ws.col.info'] == 'BearerContextSetupResponse') &
                                            (updated_messages['frame.protocols'].str.contains('e1ap', case=False,
                                                                                              na=False))
                                            ])

        bearerctxt_setup_failure = len(updated_messages[
                                           (updated_messages['_ws.col.info'] == 'BearerContextSetupFailure') &
                                           (updated_messages['frame.protocols'].str.contains('e1ap', case=False,
                                                                                             na=False))
                                           ])

        # Check for timeouts
        bearerctxt_timeout = 1 if (
                bearerctxt_setup_request > 0 and
                bearerctxt_setup_response == 0 and
                bearerctxt_setup_failure == 0
        ) else 0

        logging.debug("calculate_bearer_ctxt_stats - Completed.")

        return {
            'bearer_ctxt_attempts': bearerctxt_setup_request,
            'bearer_ctxt_success': bearerctxt_setup_response,
            'bearer_ctxt_failure': bearerctxt_setup_failure,
            'bearer_ctxt_timeout': bearerctxt_timeout,
        }

    @classmethod
    def bulk_update_stats(cls, bulk_update_data):
        try:
            fields_to_update = [
                'rrc_setup_attempts', 'rrc_setup_success', 'rrc_setup_failure', 'rrc_setup_timeout',
                'initial_ctxt_attempts', 'initial_ctxt_success', 'initial_ctxt_failure',
                'initial_ctxt_timeout',
                'bearer_ctxt_attempts', 'bearer_ctxt_success', 'bearer_ctxt_failure', 'bearer_ctxt_timeout',
                'xnap_handover_attempts', 'xnap_handover_success', 'xnap_handover_failure', 'xnap_handover_timeout',
                'f1ap_cause', 'ngap_cause', 'nas_cause',
            ]

            # Extract all unique identifiers' IDs from bulk_update_data
            identifiers_ids = {item['id'] for item in bulk_update_data}

            # Query all Identifier instances in a single query
            identifiers_to_update = Identifiers.objects.filter(pk__in=identifiers_ids)

            # Create a dictionary for quick lookup based on identifier ID
            identifiers_dict = {identifier.id: identifier for identifier in identifiers_to_update}

            # Update each instance with the corresponding values
            for update_dict in bulk_update_data:
                identifier_id = update_dict['id']
                identifier = identifiers_dict.get(identifier_id)
                if identifier:
                    for field in fields_to_update:
                        setattr(identifier, field, update_dict.get(field, None))

            # Bulk update the Identifier instances
            Identifiers.objects.bulk_update(identifiers_to_update, fields_to_update)

        except Exception as e:
            logging.error("Error during bulk update:", e)

    @classmethod
    def calculate_handover_stats(cls, updated_messages):
        logging.debug("calculate_handover_stats - Started.")

        # Extract counts for each handover-related message type
        xnap_handover_request_attempts = len(updated_messages[
                                                 (updated_messages['_ws.col.info'] == 'HandoverRequest') &
                                                 (updated_messages['frame.protocols'].str.contains('xnap', case=False,
                                                                                                   na=False))
                                                 ])

        xnap_handover_request_ack_success = len(updated_messages[
                                                    (updated_messages['_ws.col.info'] == 'HandoverRequestAcknowledge') &
                                                    (updated_messages['frame.protocols'].str.contains('xnap',
                                                                                                      case=False,
                                                                                                      na=False))
                                                    ])

        xnap_handover_failure = len(updated_messages[
                                        (updated_messages['_ws.col.info'] == 'HandoverFailure') & (
                                                updated_messages['_ws.col.info'] == 'HandoverCancel') &
                                        (updated_messages['frame.protocols'].str.contains('xnap', case=False, na=False))
                                        ])

        xnap_handover_timeout = 1 if (
                xnap_handover_request_attempts > 0 and
                xnap_handover_request_ack_success == 0 and
                xnap_handover_failure == 0
        ) else 0

        logging.debug("calculate_handover_stats - Completed.")

        return {
            'xnap_handover_attempts': xnap_handover_request_attempts,
            'xnap_handover_success': xnap_handover_request_ack_success,
            'xnap_handover_failure': xnap_handover_failure,
            'xnap_handover_timeout': xnap_handover_timeout,
        }

    @classmethod
    def get_gnb_ids(cls, file_id):
        unique_gnb_ids_with_ips = Identifiers.objects.filter(
            uploaded_file_id=file_id,
            gnb_id__isnull=False,
        ).exclude(gnb_id="").values('gnb_id', 'cucp_f1c_ip').order_by('gnb_id').distinct()
        formatted_results = [f"{pair['gnb_id']}({pair['cucp_f1c_ip']})" for pair in unique_gnb_ids_with_ips]

        return formatted_results

    # @classmethod
    # def get_cause_data(cls, updated_messages):
    #     f1ap_cause = next(iter(updated_messages['f1ap.cause_desc'].dropna()), None)
    #     ngap_cause = next(iter(updated_messages['ngap.cause_desc'].dropna()), None)
    #     nas_cause = next(iter(updated_messages['nas.cause_desc'].dropna()), None)
    #     return {
    #         'f1ap_cause': f1ap_cause,
    #         'ngap_cause': ngap_cause,
    #         'nas_cause': nas_cause,
    #     }
    @classmethod
    def get_cause_data(cls, updated_messages):
        nas_cause = next(iter(updated_messages['nas.cause_desc'].dropna()), None)
        ngap_cause = next(iter(updated_messages['ngap.cause_desc'].dropna()), None)
        f1ap_cause = next(iter(updated_messages['f1ap.cause_desc'].dropna()), None)
        rre_cause = next(iter(updated_messages['rre.cause_desc'].dropna()), None)
        rel_cause = None
        if nas_cause is not None:
            rel_cause = nas_cause
        elif ngap_cause is not None:
            rel_cause = ngap_cause
        elif f1ap_cause is not None:
            rel_cause = f1ap_cause

        return {
            'f1ap_cause': f1ap_cause,
            'ngap_cause': ngap_cause,
            'nas_cause': nas_cause,
            'rel_cause': rel_cause,
            'rre_cause': rre_cause,
        }
