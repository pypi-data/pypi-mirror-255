
import os
os.environ['POLLINATION_API_URL'] = 'https://api.staging.pollination.cloud'

import streamlit.components.v1 as components
from pollination_streamlit.selectors import get_api_client
from pollination_streamlit_io import create_study, send_results

from pollination_streamlit_viewer import viewer
import streamlit as st
api_client = get_api_client()

study = create_study('st-study',
                     api_client=api_client)

show_report = st.checkbox('Show Report')

if study:
    name, value, type = study.progress_report(show_output=show_report, 
                                              color='#f2b24d',
                                              show_status_label=True)
    if name and name.endswith('vtkjs'):
        viewer(key='model', content=value)

    # get file
    viz_bytes = study.download_artifact('visualization.vsf')
    if viz_bytes:
        send_results(key='viz', 
                     delay=50,
                     results=viz_bytes.decode('utf-8'),
                     option='subscribe-preview',
                     options={ 'delete': False })