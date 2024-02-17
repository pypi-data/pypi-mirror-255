from pollination_streamlit_io import run_command
import streamlit as st

st.header("Pollination command")
st.info('Command without trigger')
run_command(command='Circle')

st.info('Command with trigger')
num = st.slider('Number', 
                min_value=1, 
                max_value=10)

hide = st.checkbox('Hide button', value=False)
run_command(key='line-cmd', command='Line', trigger=num, hide_button=hide)
