"""Select a run and view the run details."""
import json
import streamlit as st
from pollination_streamlit.selectors import get_api_client
from pollination_streamlit_io import (run_card, run_details, select_account, select_project, select_study, select_run)

api_client = get_api_client()

account = select_account(
    'sel-account', 
    api_client
)

if account:
    project = select_project(
        'sel-project',
        api_client,
        project_owner=account.get('username')
    )

    if project:
        study = select_study(
            'sel-study',
            api_client,
            project_name=project.get('name'),
            project_owner=account.get('username')
        )

        if study:
            run = select_run(
                'sel-run',
                api_client,
                project_name=project.get('name'),
                project_owner=account.get('username'),
                job_id=study.get('id'),
            )

            if run:
                out_run = run_card(
                    'run-card',
                    api_client,
                    project_name = project.get('name'),
                    project_owner = account.get('username'),
                    run = run)

                if out_run:
                    card = run_details('run-details', 
                        api_client = api_client,
                        project_name = project.get('name'),
                        project_owner = account.get('username'),
                        run = out_run)