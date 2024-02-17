import streamlit.components.v1 as components

from pollination_streamlit_io import (get_host, epw_map)

import streamlit as st

weather_info = epw_map(latitude=20, 
                       longitude=20, 
                       style={'height': '600px', 
                              'border': '2px solid #f4f4f4',
                              'borderRadius': '5px' })

st.json(weather_info)