"""Download files from Pollination jobs aka studies."""
import json
import streamlit as st
from pollination_streamlit.selectors import get_api_client
from pollination_streamlit_io import (select_account, select_cloud_artifact, select_project, select_recipe, select_study, select_run)

import requests

api_client = get_api_client()

direct_sun_hours = open('examples/apps/files/direct_sun_hours.json')

# if 'request_params' not in st.session_state:
st.session_state['request_params'] = {
    "page": 1,
    "per-page": 25,
    "path": "outputs"
}

if 'request_path' not in st.session_state:
    st.session_state['request_path'] = [
        'projects',
        None,
        None,
        'jobs',
        None,
        'artifacts'
    ]

if 'owner' not in st.session_state:
    st.session_state['owner'] = None

if 'signed_url' not in st.session_state:
    st.session_state['signed_url'] = None

if 'response' not in st.session_state:
    st.session_state['response'] = ''

def handle_sel_account():
    account = st.session_state['sel-account']
    owner = account['username'] if 'username' in account else account['account_name']
    st.session_state['owner'] = owner
    st.session_state['request_path'][1] = owner

def handle_sel_project():
    st.session_state['request_path'][2] = st.session_state['sel-project']['name']

def handle_sel_study():
    st.session_state['request_path'][4] = st.session_state['sel-study']['id']

def handle_sel_artifact():
    artifact = st.session_state['sel-artifact']
    st.session_state['request_params']['path'] = artifact['key']
    url = "/".join(st.session_state['request_path'])
    st.session_state['signed_url'] = api_client.get(path=f'/{url}/download', params=st.session_state['request_params'])
    response = requests.get(st.session_state['signed_url'], headers=api_client.headers)
    if response.status_code is 200:
        st.session_state['response'] = response.content

account = select_account(
    'sel-account', 
    api_client,
    default_account_username='ladybug-tools',
    on_change=handle_sel_account
)

project = select_project(
    'sel-project',
    api_client,
    project_owner=st.session_state['owner'] or '',
    default_project_id="eeaef2bf-6b2b-472e-a608-d2a6af78bd20",
    on_change=handle_sel_project
)

select_study(
    'sel-study',
    api_client,
    project_name=st.session_state['sel-project']['name'] if st.session_state['sel-project'] else '',
    project_owner=st.session_state['owner'] or '',
    on_change=handle_sel_study
)

select_recipe(
    'sel-recipe',
    api_client,
    project_name=st.session_state['sel-project']['name'] if st.session_state['sel-project'] else '',
    project_owner=st.session_state['owner'] or '',
    default_recipe=json.load(direct_sun_hours)
)

select_run(
    'sel-run',
    api_client,
    project_name=st.session_state['sel-project']['name'] if st.session_state['sel-project'] else '',
    project_owner=st.session_state['owner'] or '',
    job_id=st.session_state['sel-study']['id'] if st.session_state['sel-study'] else '',
)

select_cloud_artifact(
    'sel-artifact',
    api_client,
    project_name=st.session_state['sel-project']['name'] if st.session_state['sel-project'] else '',
    project_owner=st.session_state['owner'] or '',
    study_id=st.session_state['sel-study']['id'] if st.session_state['sel-study'] else '',
    file_name_match=".*",
    on_change=handle_sel_artifact
)

st.download_button(
    label='Download File', 
    data=st.session_state['response'], 
    file_name=st.session_state['sel-artifact']['name'] if st.session_state['sel-artifact'] is not None else 'download.zip', 
    key='download-button',
    disabled=st.session_state['response'] == ''
  )

st.subheader('Selected Artifact')
st.json(st.session_state['sel-artifact'] or '{}', expanded=False)
st.subheader('Selected Recipe')
st.json(st.session_state['sel-recipe'] or '{}', expanded=False)