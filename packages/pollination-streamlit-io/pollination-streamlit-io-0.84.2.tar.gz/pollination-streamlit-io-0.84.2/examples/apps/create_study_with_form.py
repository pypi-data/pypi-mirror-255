import os
os.environ['POLLINATION_API_URL'] = 'https://api.staging.pollination.cloud'

from pollination_streamlit.selectors import get_api_client
from pollination_streamlit_io import select_recipe, recipe_inputs_form

from pollination_streamlit_viewer import viewer
import streamlit as st

api_client = get_api_client()
project_owner = 'dnaorg'
project_name = 'form'

option = st.selectbox('Select Recipe', 
             options=('Direct sun hours', 'Cumulative radiation'))

if option == 'Direct sun hours':
    default_recipe = {'owner': 'ladybug-tools', 'name': 'direct-sun-hours', 'tag': '*'}
else:
    default_recipe = {'owner': 'ladybug-tools', 'name': 'cumulative-radiation', 'tag': '*'}

recipe = select_recipe('st-recipe', api_client,
                project_owner=project_owner,
                project_name=project_name,
                default_recipe=default_recipe)

# trigger
north = st.slider('north', 0, 100, 0)
st.text(north)

if recipe:
    user_inputs = {
        'wea': ['C:/ladybug/ITA_Campobasso.162520_IGDG/ITA_Campobasso.162520_IGDG.wea', 'my_file.wea'],
        'north': north
    }

    study = recipe_inputs_form(key='st-study', 
                        api_client=api_client, 
                        project_name=project_name,
                        project_owner=project_owner,
                        recipe_filter=recipe,
                        user_inputs=user_inputs,
                        sync_change=True,
                        study_name='my study',
                        is_local=True)
    if study:
        name, value, type = study.progress_report(show_output=True,
                                            show_result=True)
        
        if name and name.endswith('vtkjs'):
            viewer(key='my-test', content=value)