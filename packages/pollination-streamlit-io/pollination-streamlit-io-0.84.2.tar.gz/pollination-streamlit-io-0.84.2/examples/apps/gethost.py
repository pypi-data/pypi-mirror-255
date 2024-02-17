import os, json
import streamlit.components.v1 as components

from pollination_streamlit_io import get_host

import streamlit as st

host = get_host()

st.write(host)