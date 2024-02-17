import os
os.environ['POLLINATION_API_URL'] = 'https://api.staging.pollination.cloud'

import streamlit as st
from pollination_streamlit.selectors import get_api_client
from pollination_streamlit_io import recipe_inputs_form

api_client = get_api_client()
recipe = {'owner': 'ladybug-tools', 'name': 'direct-sun-hours', 'tag': '0.5.14-viz'}
project_owner = 'dnaorg'
project_name = 'form'

enable_controlled = st.checkbox('User input?')
show_form = st.checkbox('Show form?')

if enable_controlled:
    controlled_values = {
      'wea': ['C:/ladybug/ITA_Campobasso.162520_IGDG/ITA_Campobasso.162520_IGDG.wea', 'hello.wea']
    }
else:
    controlled_values = None

study = recipe_inputs_form(key='st-study', 
                           api_client=api_client, 
                           project_name=project_name,
                           project_owner=project_owner,
                           recipe_filter=recipe,
                           user_inputs=controlled_values,
                           study_name='my study',
                           is_local=True,
                           show_form=show_form)

study.progress_report(refresh_interval=300, show_output=True, show_result=True)