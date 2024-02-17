import os, json
import streamlit.components.v1 as components

from pollination_streamlit.selectors import get_api_client

from pollination_streamlit_io import (select_account, select_project, select_recipe, recipe_inputs_form)

import streamlit as st

api_client = get_api_client()

account = select_account('account', api_client)

project_owner = None
if account is not None:
  if 'username' in account:
      project_owner = account['username']
  elif 'account_name' in account:
      project_owner = account['account_name']

project = select_project('project', api_client, project_owner=project_owner)

project_name = None

if project is not None:
  project_name = project['name']

  recipe = select_recipe(
    'select-recipe', 
    api_client, 
    project_name=project_name, 
    project_owner=project_owner)

  # defaults = {
  #   "cpu-count" : {
  #     "value": 25,
  #     "hidden": True
  #   }
  # }

  if recipe is not None:
    output = recipe_inputs_form(
      'recipe-inputs-form',
      api_client,
      project_name=project_name,
      project_owner=project_owner,
      # default_inputs=defaults,
      recipe=recipe
    )

    if output:
      st.json(output)