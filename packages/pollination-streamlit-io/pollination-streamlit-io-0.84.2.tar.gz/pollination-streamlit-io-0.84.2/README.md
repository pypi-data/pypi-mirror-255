# Pollination Streamlit IO

Streamlit input/output components to use with Pollination apps. This library uses 
WebView2 technology to interact with the Pollination CAD plugins.

## Controls
* get_geometry = Get geometry as a json object from the host CAD platform.
* get_hbjson = Get an hbjson model from the host CAD plarform.
* send_geometry = Send geometry as a json object to the host CAD platform.
* send_hbjson = Send hbjson model to the host CAD platform.

## UX (for developers)
It is easy to use.

How to show pollination controls only if platform is Rhino

### Example of url `https://my-special-app.something`
```python
from pollination_streamlit_io import {}

# get host name
platform = special.get_host()

if platform == 'Rhino':
    # add your logic here with pollination_streamlit_io
```

### Example of mini-app Rhino > Streamlit

```python
import streamlit as st
from pollination_streamlit_io import { get_geometry }

st.subheader("Pollination, Get Pollination Model")
model = get_hbjson(key="foo")
st.json(model)
```

### Example of mini-app Streamlit > Rhino

```python
import streamlit as st
import json
from pollination_streamlit_io import { send_geometry }

st.subheader("Pollination, Bake Geometry Button")

# array of ladybug geometry dictionaries or 
# a ladybug geometry dictionary
data_to_pass = [{
    "type": "Mesh3D",
    "vertices": [(0, 0, 0), (10, 0, 0), (0, 10, 0)],
    "faces": [(0, 1, 2)],
    "colors": [{"r": 255, "g": 0, "b": 0}]
}, 
{ 
    'type': 'Polyline2D',
     'vertices': [[5, 5], [35, 5], [5, 35]] 
}]

send_geometry(key='bar', geometry=data_to_pass)
```

## Make (for developers)
Use `make generate-frontend` to create build from react

Create a virtual env in tests folder. Install requirements.txt with `pip install -r requirements.txt`. Install the package in dev mode with `pip install -e ../.`

Use `make dev-install-package` to update deps of tests
