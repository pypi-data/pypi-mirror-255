import streamlit as st
from pollination_streamlit_io import get_geometry

st.header('Layout test')

col1, col2 = st.columns(2)

# button generic settings
options = {
    "subscribe" : { "show": False, "selected": False }, 
    "selection" : { "show": False, "selected": True }, 
    "preview" : { "show": True, "selected": True }
}

full_width = True

with col1:
    geo1 = get_geometry(key='btn-1', 
                        label='Select Study Building',
                        options=options,
                        full_width=full_width)
    geo2 = get_geometry(key='btn-2', 
                        label='Select Ground Surface', 
                        options=options,
                        full_width=full_width)
with col2:
    geo3 = get_geometry(key='btn-3', 
                        label='Select Surrounds/context', 
                        options=options,
                        full_width=full_width)
    geo4 = get_geometry(key='btn-4', 
                        label='Select Presentation Plane', 
                        options=options,
                        full_width=full_width)
