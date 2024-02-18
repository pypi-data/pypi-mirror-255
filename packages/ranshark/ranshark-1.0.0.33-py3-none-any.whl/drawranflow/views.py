# views.py
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import distribution

from django.db import connection
from django.utils import timezone
import pyshark
from django.conf import settings
from django.db.models import Sum, F
from django.http import JsonResponse, FileResponse, HttpResponseServerError, HttpResponseRedirect
from django.shortcuts import render
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from drawranflow.servicelogic.handlers.processPacketslte import packetHandler as phlte

from drawranflow.servicelogic.handlers.processPacketssa import packetHandler as ph
from .models import UploadedFile, Identifiers, Message, Identifierslte, Messagelte, IpvsEntityName
from .servicelogic.handlers.files_handler_sa import FileHandlers as fh
# from .servicelogic.handlers.nsa_files_handler import FileHandlers as nsafh
from .servicelogic.handlers.files_handler_lte import FileHandlers as fhlte

from .servicelogic.handlers.statsHandler_sa import computeStats as sh
from .servicelogic.handlers.statsHandler_lte import computeStats as shlte

from django.db.models import IntegerField
from django.db.models.functions import Cast

BASE_DIR = getattr(settings, 'BASE_DIR', None)
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', None)


def about(request):
    # Get the installed package version dynamically
    # app_version = distribution("ranshark").version
    app_version = "test"
    return render(request, 'about.html', {'app_version': app_version})


# home Landing page
def home(request):
    return render(request, 'home.html')


# upload_file Handling upload file
def upload_file(request):
    messages = {}
    if request.method == 'POST':
        file = request.FILES.get('file_upload')
        network = request.POST.get('network')

        messages = fh.upload_pcap_file(file=file, network=network)
    return JsonResponse(messages)


# delete_file Handling delete file request
def delete_file(request, item_id):
    try:
        item = UploadedFile.objects.get(id=item_id)
        # Delete the associated file from the media path
        if item:
            file_path = item.filename
            file_path = os.path.join(settings.MEDIA_ROOT, file_path)
            logging.debug(f"files to be deleted {file_path}")
            if os.path.exists(file_path):
                fh.delete_files(file_path)
                # Delete the item from the database
            item.delete()

        return JsonResponse({'message_type': 'success', 'message_text': f'{item.filename} deleted successfully'},
                            status=200)
    except UploadedFile.DoesNotExist:
        return JsonResponse({'message': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': f'Error: {str(e)}'}, status=500)


def process_file_async(item):
    try:
        file_path = os.path.join(MEDIA_ROOT, item.filename)
        f = f'{file_path}'
        tmp = f'{item.filename}'.split('.')[0]
        csv = f'{MEDIA_ROOT}/{tmp}.csv'
        if item.network == "5G-SA":
            ph(input_pcap=f, output_csv=csv, item_id=item.id).capture_packets_and_save_to_csv()
        else:
            # phnsa(input_pcap=f, output_csv=csv, item_id=item.id).capture_packets_nsa_and_save_to_csv()
            phlte(input_pcap=f, output_csv=csv, item_id=item.id).capture_packets_and_save_to_csv()

        return {'message_type': 'success', 'message_text': f'{item.filename} process started successfully'}
    except Exception as e:
        return {'message_type': 'error', 'message': f'Error: {str(e)}'}


def process_file(request, item_id):
    try:
        item = UploadedFile.objects.get(id=item_id)
        if item:
            setattr(item, 'processDate', timezone.now())
            setattr(item, 'processed', True)
            item.save()

            with ThreadPoolExecutor() as executor:
                # Submit the task to the thread pool
                future = executor.submit(process_file_async, item)

        return JsonResponse(
            {'message_type': 'success', 'message_text': f'{item.filename} process completed successfully'}, status=200)
    except UploadedFile.DoesNotExist:
        return JsonResponse({'message_type': 'error', 'message': 'file not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message_type': 'error', 'message': f'Error: {str(e)}'}, status=500)


# check_file_existence to check if the file is already exists
def check_file_existence(request):
    file_exists = False
    if request.method == "POST":
        file_name = request.POST.get('file_name')
        try:
            if UploadedFile.objects.filter(filename=file_name).exists():
                # File exists in the database
                file_exists = True
        except Exception as e:
            # Handle any exceptions or errors
            logging.error("Error checking file existence:", str(e))
    return JsonResponse({'file_exists': file_exists})


# streaming_table_view streaming the list view
def streaming_table_view_bkup(request):
    # Retrieve data from the MainTable model
    id = request.GET.get('id')
    identifiers_table_data = Identifiers.objects.filter(uploaded_file_id=id).order_by('id').values()

    # Convert the data to a list
    data = list(identifiers_table_data)
    return JsonResponse(data, safe=False)


from django.db.models import Subquery, OuterRef


def streaming_table_view(request):
    # Retrieve data from the MainTable model
    id = request.GET.get('id')

    # Update Identifiers only if node_name is not None
    identifiers_table_data = Identifiers.objects.filter(uploaded_file_id=id).order_by('id').values()
    # Convert the data to a list of dictionaries with the expected format
    # print(identifiers_table_data)
    data = [
        {
            'id': item['id'],
            'gnb_id': item['gnb_id'],
            'local_cell': None if item['local_cell'] == 'nan' else item['local_cell'],
            'c_rnti': item['c_rnti'],
            'gnb_du_ue_f1ap_id': item['gnb_du_ue_f1ap_id'],
            'gnb_cu_ue_f1ap_id': None if item['gnb_cu_ue_f1ap_id'] == 'nan' else item['gnb_cu_ue_f1ap_id'],
            'gnb_cu_cp_ue_e1ap_id': None if item['gnb_cu_cp_ue_e1ap_id'] == 'nan' else item['gnb_cu_cp_ue_e1ap_id'],
            'gnb_cu_up_ue_e1ap_id': None if item['gnb_cu_up_ue_e1ap_id'] == 'nan' else item['gnb_cu_up_ue_e1ap_id'],
            'ran_ue_ngap_id': None if item['ran_ue_ngap_id'] == 'nan' else item['ran_ue_ngap_id'],
            'amf_ue_ngap_id': None if item['amf_ue_ngap_id'] == 'nan' else item['amf_ue_ngap_id'],
            'xnap_src_ran_id': None if item['xnap_src_ran_id'] == 'nan' else item['xnap_src_ran_id'],
            'xnap_trgt_ran_id': None if item['xnap_trgt_ran_id'] == 'nan' else item['xnap_trgt_ran_id'],
            'pci': None if item['pci'] == 'nan' else item['pci'],
            'plmn': None if item['plmn'] == 'nan' else item['plmn'],
            'tmsi': None if item['tmsi'] == 'nan' else item['tmsi'],
            'f1ap_cause': None if item['f1ap_cause'] == 'nan' else item['f1ap_cause'],
            'rel_cause': 'rrc setup timed out' if item['rrc_setup_timeout'] == '1' else item['rel_cause'],
            'ngap_cause': None if item['ngap_cause'] == 'nan' else item['ngap_cause'],
            'nas_cause': None if item['nas_cause'] == 'nan' else item['nas_cause'],
            'du_f1c_ip': None if item['du_f1c_ip'] == 'nan' else item['du_f1c_ip'],
            'frame_time': None if item['frame_time'] == 'nan' else item['frame_time'],
            'rre_cause': None if item['rre_cause'] == 'nan' else item['rre_cause'],
            'old_crnti': None if item['old_crnti'] == 'nan' else item['old_crnti'],

        }
        for item in identifiers_table_data
    ]

    return JsonResponse(data, safe=False)


def streaming_table_view_nsa(request):
    # Retrieve data from the MainTable model
    id = request.GET.get('id')

    identifiers_table_data = Identifierslte.objects.filter(uploaded_file_id=id).order_by('id').values()

    # Convert the data to a list of dictionaries with the expected format
    data = [
        {
            'id': item['id'],
            'gnb_id': None if item['gnb_id'] == 'nan' else item['gnb_id'],
            'c_rnti': item['c_rnti'],
            'enb_ue_s1ap_id': item['enb_ue_s1ap_id'],
            'mme_ue_s1ap_id': None if item['mme_ue_s1ap_id'] == 'nan' else item['mme_ue_s1ap_id'],
            'x2ap_ue_ran_id': None if item['x2ap_ue_ran_id'] == 'nan' else item['x2ap_ue_ran_id'],
            'x2ap_5g_ran_id': None if item['x2ap_5g_ran_id'] == 'nan' else item['x2ap_5g_ran_id'],
            'pci': None if item['pci'] == 'nan' else item['pci'],
            'plmn': None if item['plmn'] == 'nan' else item['plmn'],
            'tmsi': None if item['tmsi'] == 'nan' else item['tmsi'],

        }
        for item in identifiers_table_data
    ]
    return JsonResponse(data, safe=False)


# display_streaming_table streaming table view as list
def display_streaming_table(request, network, id):
    if network == "5G-SA":
        html = "listView_sa.html"
        context = {
            'id': id,
            'network': network,
        }
    else:
        html = "listView_lte.html"

        context = {
            'id': id,
            'network': network,
        }
    return render(request, html, context)


# fetch_associated_data fetching all messages related to a Call
def fetch_associated_data(request, main_id):
    try:

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE messagesa
                SET ip_src = (
                    SELECT node_name FROM ipvsentityname WHERE messagesa.ip_src = ipvsentityname.ip LIMIT 1
                )
                WHERE EXISTS (
                    SELECT 1 FROM ipvsentityname WHERE messagesa.ip_src = ipvsentityname.ip
                ) AND identifiers_id= %s;
            """,(main_id,))
            cursor.execute("""
                UPDATE messagesa
                SET ip_dst = (
                    SELECT node_name FROM ipvsentityname WHERE messagesa.ip_dst = ipvsentityname.ip LIMIT 1
                )
                WHERE EXISTS (
                    SELECT 1 FROM ipvsentityname WHERE messagesa.ip_dst = ipvsentityname.ip
                ) AND identifiers_id= %s;
            """,(main_id,))

        messages = Message.objects.filter(identifiers=main_id).order_by('frame_time')
        messages_list = []  # List to store all associated data for the main_id

        for message in messages:
            message_data = {
                'message_key': message.id,
                'frame_number': message.frame_number,
                'frame_time': str(message.frame_time),
                'ip_src': message.ip_src,
                'ip_dst': message.ip_dst,
                'protocol': message.protocol,
                'f1_proc': message.f1_proc,
                'e1_proc': message.e1_proc,
                'ng_proc': message.ng_proc,
                'c1_rrc': message.c1_rrc,
                'c2_rrc': message.c2_rrc,
                'mm_message_type': message.mm_message_type,
                'sm_message_type': message.sm_message_type,
                'message': message.message,
                'src_node': message.src_node,
                'dst_node': message.dst_node,
                'message_json': message.message_json,
                'c_rnti': message.c_rnti,
                'gnb_du_ue_f1ap_id': message.gnb_du_ue_f1ap_id,
                'gnb_cu_ue_f1ap_id': message.gnb_cu_ue_f1ap_id,
                'gnb_cu_cp_ue_e1ap_id': message.gnb_cu_cp_ue_e1ap_id,
                'gnb_cu_up_ue_e1ap_id': message.gnb_cu_up_ue_e1ap_id,
                'ran_ue_ngap_id': message.ran_ue_ngap_id,
                'amf_ue_ngap_id': message.amf_ue_ngap_id,
                'xnap_src_ran_id': message.xnap_src_ran_id,
                'xnap_trgt_ran_id': message.xnap_trgt_ran_id,
            }

            # Use message_data as needed

            messages_list.append(message_data)
        return messages_list

    except Message.DoesNotExist:
        # Handle the case where the message with the given id is not found
        return None
    except Exception as e:
        # Handle other exceptions
        raise e


def fetch_associated_data_nsa(request, main_id):
    try:
        messages = Messagelte.objects.filter(identifiers=main_id).order_by('frame_time')
        messages_list = []  # List to store all associated data for the main_id

        for message in messages:
            message_data = {
                'message_key': message.id,
                'frame_number': message.frame_number,
                'ip_src': message.ip_src,
                'ip_dst': message.ip_dst,
                'message': message.message,
                'src_node': message.src_node,
                'dst_node': message.dst_node,
                'message_json': message.message_json,
                'c_rnti': message.c_rnti,
            }

            # Use message_data as needed

            messages_list.append(message_data)
        return messages_list

    except Message.DoesNotExist:
        # Handle the case where the message with the given id is not found
        return None
    except Exception as e:
        # Handle other exceptions
        raise e


@csrf_exempt
def prepare_download_pcap(request):
    uploadfile = ""

    try:
        # Retrieve main_id from the request's GET parameters
        main_id = request.GET.get('main_id')
        logging.debug(f"main id: {main_id}")

        # Fetch data based on the main_id from the Identifiers table
        identifier_data = fh.fetch_identifier_data(main_id)

        # Construct a filter based on the identifier data
        if identifier_data:
            pcap_filter = fh.construct_pcap_filter(identifier_data)
            logging.debug(f"identifier_data: {identifier_data}")

            if pcap_filter:
                uploadfile = UploadedFile.objects.get(id=identifier_data.uploaded_file_id)

                filename = uploadfile.filename
                f = filename.split('.')
                # Filter the original pcap file and save the filtered file
                original_pcap_path = os.path.join(settings.MEDIA_ROOT, filename)

                outputfile = os.path.join(settings.MEDIA_ROOT,
                                          f"{f[0]}_{identifier_data.c_rnti}_{identifier_data.gnb_du_ue_f1ap_id}.pcap")
                logging.debug(f'original_pcap_path={original_pcap_path}, outputfile={outputfile}')
                outputfile = fh.filter_pcap(original_pcap_path, pcap_filter, outputfile)

                # Check if the file exists before trying to open it
                if os.path.exists(outputfile) and outputfile:
                    response = FileResponse(open(outputfile, 'rb'), content_type="application/vnd.tcpdump.pcap")
                    response[
                        "Content-Disposition"] = f'attachment; filename="{smart_str(os.path.basename(outputfile))}"'
                    return response
                else:
                    return JsonResponse({'error': 'Filtered file not found'}, status=404)
        else:
            return JsonResponse({'error': 'Identifier data not found'}, status=404)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def prepare_download_pcap_nsa(request):
    uploadfile = ""

    try:
        # Retrieve main_id from the request's GET parameters
        main_id = request.GET.get('main_id')
        logging.debug(f"main id: {main_id}")

        # Fetch data based on the main_id from the Identifiers table
        identifier_data = fhlte.fetch_identifier_data(main_id)

        # Construct a filter based on the identifier data
        if identifier_data:
            pcap_filter = fhlte.construct_pcap_filter(identifier_data)
            logging.debug(f"identifier_data: {identifier_data}")

            if pcap_filter:
                uploadfile = UploadedFile.objects.get(id=identifier_data.uploaded_file_id)

                filename = uploadfile.filename
                f = filename.split('.')
                # Filter the original pcap file and save the filtered file
                original_pcap_path = os.path.join(settings.MEDIA_ROOT, filename)

                outputfile = os.path.join(settings.MEDIA_ROOT,
                                          f"{f[0]}_{identifier_data.c_rnti}_{identifier_data.enb_ue_s1ap_id}.pcap")
                logging.debug(f'original_pcap_path={original_pcap_path}, outputfile={outputfile}')
                outputfile = fhlte.filter_pcap(original_pcap_path, pcap_filter, outputfile)

                # Check if the file exists before trying to open it
                if os.path.exists(outputfile) and outputfile:
                    response = FileResponse(open(outputfile, 'rb'), content_type="application/vnd.tcpdump.pcap")
                    response[
                        "Content-Disposition"] = f'attachment; filename="{smart_str(os.path.basename(outputfile))}"'
                    return response
                else:
                    return JsonResponse({'error': 'Filtered file not found'}, status=404)
        else:
            return JsonResponse({'error': 'Identifier data not found'}, status=404)
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# fetch_packet_data fetching packet data
def fetch_packet_data(request):
    main_id = request.GET.get('main_id')
    logging.debug(f"main id: {main_id}")

    # Fetch data based on the main_id from the Identifiers table
    identifier_data = fh.fetch_identifier_data(main_id)
    original_pcap_path = None
    # Construct a filter based on the identifier data
    if identifier_data:
        logging.debug(f"identifier_data: {identifier_data}")
        uploadfile = UploadedFile.objects.get(id=identifier_data.uploaded_file_id)
        filename = uploadfile.filename
        original_pcap_path = os.path.join(settings.MEDIA_ROOT, filename)

    frame_numbers = [message.frame_number for message in Message.objects.filter(
        identifiers_id=identifier_data.id
    ).order_by('frame_time')]

    if frame_numbers and original_pcap_path:
        frame_filter = '||'.join([f'frame.number=={fn}' for fn in frame_numbers])
        logging.debug(f"frame_filter - {frame_filter}")

        try:
            # Use PyShark to filter packets based on frame numbers
            if os.path.exists(original_pcap_path):
                with pyshark.FileCapture(original_pcap_path, display_filter=frame_filter) as packets:
                    packets.set_debug()
                    for packet in packets:
                        pduType = sh.packetLayers(packet=packet)
                        test = sh.packet_to_json(pduType)
                        if test:
                            # Find the message associated with the current frame number
                            matching_message = next(
                                (message for message in Message.objects.filter(identifiers_id=identifier_data.id) if
                                 message.frame_number == int(packet.frame_info.number)), None)
                            if matching_message:
                                matching_message.message_json = test
                                matching_message.save()
        except Exception as e:
            logging.error(f"Error capturing packets: {e}")

    associated_data = fetch_associated_data(request, main_id)
    logging.debug(f"associated_data- {associated_data}")

    # Render the draw-sequence view with the associated data
    if associated_data:
        associated_data = json.dumps(associated_data)
        context = {'main_id': main_id, 'associated_data': associated_data}
        return render(request, 'draw_sequence_sa.html', context)
    else:
        return render(request, 'draw_sequence_sa.html')


def fetch_packet_data_nsa(request):
    main_id = request.GET.get('main_id')
    logging.debug(f"main id: {main_id}")

    # Fetch data based on the main_id from the Identifiers table
    identifier_data = fhlte.fetch_identifier_data(main_id)
    original_pcap_path = None
    # Construct a filter based on the identifier data
    if identifier_data:
        logging.debug(f"identifier_data: {identifier_data}")
        uploadfile = UploadedFile.objects.get(id=identifier_data.uploaded_file_id)
        filename = uploadfile.filename
        original_pcap_path = os.path.join(settings.MEDIA_ROOT, filename)

    frame_numbers = [message.frame_number for message in Messagelte.objects.filter(
        identifiers_id=identifier_data.id
    ).order_by('frame_time')]

    if frame_numbers and original_pcap_path:
        frame_filter = '||'.join([f'frame.number=={fn}' for fn in frame_numbers])
        logging.debug(f"frame_filter - {frame_filter}")

        try:
            # Use PyShark to filter packets based on frame numbers
            if os.path.exists(original_pcap_path):
                with pyshark.FileCapture(original_pcap_path, display_filter=frame_filter) as packets:
                    packets.set_debug()
                    for packet in packets:
                        pduType = sh.packetLayers(packet=packet)
                        test = sh.packet_to_json(pduType)
                        if test:
                            # Find the message associated with the current frame number
                            matching_message = next(
                                (message for message in Messagelte.objects.filter(identifiers_id=identifier_data.id) if
                                 message.frame_number == int(packet.frame_info.number)), None)
                            if matching_message:
                                matching_message.message_json = test
                                matching_message.save()
        except Exception as e:
            logging.error(f"Error capturing packets: {e}")

    associated_data = fetch_associated_data(request, main_id)
    logging.debug(f"associated_data- {associated_data}")

    # Render the draw-sequence view with the associated data
    if associated_data:
        associated_data = json.dumps(associated_data)
        context = {'main_id': main_id, 'associated_data': associated_data}
        return render(request, 'draw_sequence_sa.html', context)
    else:
        return render(request, 'draw_sequence_sa.html')


def draw_sequence_view(request, main_id):
    if main_id is not None:
        filter_string = ""
        # Fetch associated data using  fetch_associated_data function
        associated_data = fetch_associated_data(request, main_id)
        identifier_data = fh.fetch_identifier_data(main_id)
        if identifier_data:
            filter_string = fh.construct_pcap_filter(identifier_data)
        # Render the draw-sequence view with the associated data
        logging.debug(f"associated_data- {associated_data}")

        associated_data = json.dumps(associated_data)
        logging.debug(f"associated_data- {associated_data}")
        context = {'main_id': main_id, 'associated_data': associated_data, 'filter_string': filter_string}

        return render(request, 'draw_sequence_sa.html', context)
    else:
        return render(request, 'draw_sequence_sa.html')


def draw_sequence_view_nsa(request, main_id):
    if main_id is not None:
        filter_string = ""
        # Fetch associated data using  fetch_associated_data function
        associated_data = fetch_associated_data_nsa(request, main_id)
        identifier_data = fhlte.fetch_identifier_data(main_id)
        if identifier_data:
            filter_string = fhlte.construct_pcap_filter(identifier_data)
        # # Render the draw-sequence view with the associated data
        # logging.debug(f"associated_data- {associated_data}")

        associated_data = json.dumps(associated_data)
        logging.debug(f"associated_data- {associated_data}")
        context = {'main_id': main_id, 'associated_data': associated_data, 'filter_string': filter_string}

        return render(request, 'draw_sequence_lte.html', context)
    else:
        return render(request, 'draw_sequence_lte.html')


def get_updated_table_data(request):
    # Query the UploadedFile model and prepare data to send as JSON
    upload_table_data = UploadedFile.objects.all().order_by('id')

    # Convert the data to a list of dictionaries with the expected format
    data = [
        {
            'id': item.id,
            'filename': item.filename,
            'uploadDate': item.uploadDate if item.uploadDate else None,
            'processDate': item.processDate if item.processDate else None,
            'processed': item.processed,
            'completeAt': item.completeAt if item.completeAt else None,
            'completed': item.completed,
            'isAnalysisComplete': item.isAnalysisComplete,
            'processing_status': item.processing_status,
            'network': item.network

        }
        for item in upload_table_data
    ]
    return JsonResponse(data, safe=False)


def show_stats(request, id):
    try:
        upload_file_id = id
        cumulative_stats_list = []
        unique_cucp_ips = sh.get_gnb_ids(id)

        category_prefixes = ['rrc_setup', 'initial_ctxt', 'bearer_ctxt', 'xnap_handover']
        sub_catogoy = ['attempts', 'success', 'failure', 'timeout']

        for cumulative_stat in get_cumulative_stats(upload_file_id, category_prefixes, "sa"):
            cucp_ip_key = f"{cumulative_stat['gnb_id']}-{cumulative_stat['cucp_f1c_ip']}"
            cumulative_stats_dict = {'CUCP': cucp_ip_key}

            for prefix in category_prefixes:
                attempts = int(cumulative_stat.get(f'{prefix}_attempts_count', 0))
                success = int(cumulative_stat.get(f'{prefix}_success_count', 0))
                failure = int(cumulative_stat.get(f'{prefix}_failure_count', 0))
                timeout = int(cumulative_stat.get(f'{prefix}_timeout_count', 0))

                cumulative_stats_dict[f'{prefix}_Attempts'] = {'Count': attempts, 'CRNTI': []}
                cumulative_stats_dict[f'{prefix}_Success'] = {'Count': success, 'CRNTI': []}
                cumulative_stats_dict[f'{prefix}_Failure'] = {'Count': failure, 'CRNTI': []}
                cumulative_stats_dict[f'{prefix}_Timeout'] = {'Count': timeout, 'CRNTI': []}

                filters = {
                    'uploaded_file_id': upload_file_id,
                    'gnb_id': cumulative_stat['gnb_id'],
                    'cucp_f1c_ip': cumulative_stat['cucp_f1c_ip'],
                }

                for status in ['attempts', 'success', 'failure', 'timeout']:
                    if eval(f'{status} > 0'):
                        entries = Identifiers.objects.filter(**filters, **{f'{prefix}_{status}__gt': 0})
                        cumulative_stats_dict[f'{prefix}_{status.capitalize()}']['CRNTI'] = [
                            '-'.join(map(str, entry))
                            for entry in entries.values_list('id', 'c_rnti', 'gnb_du_ue_f1ap_id')
                        ]

            cumulative_stats_list.append(cumulative_stats_dict)

        context = {
            'cumulative_stats_list': cumulative_stats_list,
            'cucp_ips': unique_cucp_ips,
            'categories': category_prefixes,
            'sub_categories': sub_catogoy
        }
        return render(request, 'showStats_sa.html', context)

    except Exception as e:
        logging.error(f"Error in show_stats view: {e}")
        return HttpResponseServerError("An error occurred while processing your request.")


def get_cumulative_stats(upload_file_id, category_prefixes, network):
    annotations = {}
    for prefix in category_prefixes:
        annotations[f'{prefix}_attempts_count'] = Sum(Cast(F(f'{prefix}_attempts'), output_field=IntegerField()))
        annotations[f'{prefix}_success_count'] = Sum(Cast(F(f'{prefix}_success'), output_field=IntegerField()))
        annotations[f'{prefix}_failure_count'] = Sum(Cast(F(f'{prefix}_failure'), output_field=IntegerField()))
        annotations[f'{prefix}_timeout_count'] = Sum(Cast(F(f'{prefix}_timeout'), output_field=IntegerField()))
    if network == 'sa':
        cumulative_stats = Identifiers.objects.filter(uploaded_file_id=upload_file_id) \
            .values('gnb_id', 'cucp_f1c_ip').annotate(**annotations)
    else:
        cumulative_stats = Identifierslte.objects.filter(uploaded_file_id=upload_file_id) \
            .values('gnb_id', 'cucp_f1c_ip').annotate(**annotations)
    return cumulative_stats


def show_stats_lte(request, id):
    try:
        upload_file_id = id
        cumulative_stats_list = []
        unique_cucp_ips = shlte.get_gnb_ids(id)

        category_prefixes = ['rrc_setup', 'initial_ctxt', 'x2ap_sgNBadd', 's1ap_ho', 'x2ap_ho']
        sub_catogoy = ['attempts', 'success', 'failure', 'timeout']

        for cumulative_stat in get_cumulative_stats(upload_file_id, category_prefixes, "lte"):
            cucp_ip_key = f"{cumulative_stat['gnb_id']}-{cumulative_stat['cucp_f1c_ip']}"
            cumulative_stats_dict = {'CUCP': cucp_ip_key}

            for prefix in category_prefixes:
                attempts = int(cumulative_stat.get(f'{prefix}_attempts_count', 0))
                success = int(cumulative_stat.get(f'{prefix}_success_count', 0))
                failure = int(cumulative_stat.get(f'{prefix}_failure_count', 0))
                timeout = int(cumulative_stat.get(f'{prefix}_timeout_count', 0))

                cumulative_stats_dict[f'{prefix}_Attempts'] = {'Count': attempts, 'CRNTI': []}
                cumulative_stats_dict[f'{prefix}_Success'] = {'Count': success, 'CRNTI': []}
                cumulative_stats_dict[f'{prefix}_Failure'] = {'Count': failure, 'CRNTI': []}
                cumulative_stats_dict[f'{prefix}_Timeout'] = {'Count': timeout, 'CRNTI': []}

                filters = {
                    'uploaded_file_id': upload_file_id,
                    'gnb_id': cumulative_stat['gnb_id'],
                    'cucp_f1c_ip': cumulative_stat['cucp_f1c_ip'],
                }

                for status in ['attempts', 'success', 'failure', 'timeout']:
                    if eval(f'{status} > 0'):
                        entries = Identifierslte.objects.filter(**filters, **{f'{prefix}_{status}__gt': 0})
                        cumulative_stats_dict[f'{prefix}_{status.capitalize()}']['CRNTI'] = [
                            '-'.join(map(str, entry))
                            for entry in entries.values_list('id', 'c_rnti', 'enb_ue_s1ap_id')
                        ]

            cumulative_stats_list.append(cumulative_stats_dict)

        context = {
            'cumulative_stats_list': cumulative_stats_list,
            'cucp_ips': unique_cucp_ips,
            'categories': category_prefixes,
            'sub_categories': sub_catogoy
        }
        return render(request, 'showStats_lte.html', context)

    except Exception as e:
        logging.error(f"Error in show_stats view: {e}")
        return HttpResponseServerError("An error occurred while processing your request.")


from .forms import UploadFileForm
from django.utils.html import escapejs


def uploadNodeRefFile(request):
    if request.method == 'POST':
        file = request.FILES.get('file_upload')

        if file.name:
            handle_uploaded_file(file)
        else:
            print(file.errors)  # Print form errors
    else:
        form = UploadFileForm()
        node_data = IpvsEntityName.objects.all().order_by('id').values()
        data = {'node_data': (list(node_data))}
    return render(request, 'files_upload.html',data)


import pandas as pd


def handle_uploaded_file(f):
    # Read the Excel file
    print(f)
    df = pd.read_excel(f)
    df = df.drop_duplicates()
    IpvsEntityName.objects.all().delete()

    # Iterate over the DataFrame rows
    for index, row in df.iterrows():
        # Create a new instance of the model for each row
        instance = IpvsEntityName(
            ip=row['ip'],
            node_name=row['node_name'],
        )
        # Save the instance to the DB
        instance.save()
