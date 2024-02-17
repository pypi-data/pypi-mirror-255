import os, json
import streamlit.components.v1 as components

from pollination_streamlit_io import (manage_settings)

import streamlit as st

settings = manage_settings('foo', settings={
	"earth_anchor": {"lat": 41.12345, "lon": 15.23456},
	"units": "Inches",
	"layers":["Pollination","Ladybug"],
	"tolerance": 0.001,
	"angle_tolerance": 2.0
})

st.json(settings)