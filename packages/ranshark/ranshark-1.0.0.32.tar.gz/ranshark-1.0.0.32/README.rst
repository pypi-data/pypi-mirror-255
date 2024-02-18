====================
5G RAN PCAP Analyser
====================

Quick Start
===========
1. Add drawranflow to your INSTALLED_APPS settings like below
    INSTALLED_APPS= [
        .....
        "drawranflow",
        ]
2. Add url path as below 

    path('drawranflow/', include('drawranflow.urls')),

3. Add project settings.py with MEDIA_ROOT like below

   MEDIA_ROOT = BASE_DIR/'drawranflow/pcapfiles'


