from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about', views.about, name='about'),

    # File upload and checking the existence and refresh it if required.
    path('upload_file/', views.upload_file, name='upload_file'),
    path('delete_file/<int:item_id>', views.delete_file, name='delete_file'),
    path('process_file/<int:item_id>', views.process_file, name='process_file'),


    path('get_updated_table_data/', views.get_updated_table_data, name='get_updated_table_data'),
    path('check_file_existence/', views.check_file_existence, name='check_file_existence'),

   # path('upload_file/check_file_existence/', views.check_file_existence, name='check_file_existence'),

    # Display processed calls
    path('display-streaming-table/<str:network>/<int:id>', views.display_streaming_table, name='display_streaming_table'),
    path('display-streaming-table/5G-SA/streaming-table-view/', views.streaming_table_view, name='streaming_table_view'),
    path('display-streaming-table/5G-NSA/streaming-table-view/', views.streaming_table_view_nsa, name='streaming_table_view_nsa'),

    path('display-streaming-table/fetch-associated-data/<int:main_id>/', views.fetch_associated_data, name='fetch_associated_data'),
    path('display-streaming-table/5G-SA/draw-sequence/<int:main_id>/', views.draw_sequence_view, name='draw_sequence_view'),
    path('display-streaming-table/5G-NSA/draw-sequence/<int:main_id>/', views.draw_sequence_view_nsa, name='draw_sequence_view'),
    path('display-streaming-table/fetch-associated-data/5G-NSA/<int:main_id>/', views.fetch_associated_data_nsa,
         name='fetch_associated_data_nsa'),

    path('display-streaming-table/draw-sequence/prepare-download-pcap/', views.prepare_download_pcap, name='prepare_download_pcap'),
    path('display-streaming-table/draw-sequence/fetch-packet-data/', views.fetch_packet_data,
         name='fetch-packet-data'),
    path('display-streaming-table/draw-sequence/fetch-packet-data/5G-NSA/', views.fetch_packet_data_nsa,
         name='fetch-packet-data'),
    path('display-streaming-table/draw-sequence/prepare-download-pcap/5G-NSA/', views.prepare_download_pcap_nsa,
         name='prepare_download_pcap_nsa'),

    #  path('showCucpWiseStats/<int:id>',views.showCucpWiseStats,name='cucps'),

    path('show-stats/5G-SA/<int:id>', views.show_stats, name='show-stats'),
    path('show-stats/5G-NSA/<int:id>', views.show_stats_lte, name='show-stats'),

    path('files_upload', views.uploadNodeRefFile, name='5gfile'),

]


