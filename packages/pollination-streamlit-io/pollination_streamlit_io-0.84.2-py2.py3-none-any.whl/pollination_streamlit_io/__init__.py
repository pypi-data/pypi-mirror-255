import base64
import datetime
import os
from typing import Callable, Dict, Tuple

from streamlit import session_state as _state

from streamlit.components.v1 import components as _components

from pollination_streamlit.interactors import ApiClient
from pollination_streamlit.api.jobs import JobsAPI

from .components_callbacks import register_callback
from .utils import _apply_mapping
from typing import Union
from pathlib import Path
import re

_RELEASE = True

if not _RELEASE:
    _get_host = _components.declare_component("get_host", url="http://localhost:3000")
    _manage_settings = _components.declare_component("manage_settings", url="http://localhost:3000")
    _get_geometry = _components.declare_component("get_geometry", url="http://localhost:3000")
    _recipe_inputs_form = _components.declare_component("recipe_inputs_form", url="http://localhost:3000")
    _get_hbjson = _components.declare_component("get_hbjson", url="http://localhost:3000")
    _study_progress = _components.declare_component("study_progress", url="http://localhost:3000")
    _send_geometry = _components.declare_component("send_geometry", url="http://localhost:3000")
    _create_study = _components.declare_component("create_study", url="http://localhost:3000")
    _send_hbjson = _components.declare_component("send_hbjson", url="http://localhost:3000")
    _auth_user = _components.declare_component("auth_user", url="http://localhost:3000")
    _send_results = _components.declare_component("send_results", url="http://localhost:3000")
    _select_account = _components.declare_component("select_account", url="http://localhost:3000")
    _select_run = _components.declare_component("select_run", url="http://localhost:3000")
    _select_study = _components.declare_component( "select_study", url="http://localhost:3000")
    _select_recipe = _components.declare_component("select_recipe", url="http://localhost:3000")
    _select_project = _components.declare_component("select_project", url="http://localhost:3000")
    _select_cloud_artifact = _components.declare_component("select_cloud_artifact", url="http://localhost:3000")
    _epw_map = _components.declare_component("epw_map", url="http://localhost:3000")
    _read_local_file = _components.declare_component("read_local_file", url="http://localhost:3000")
    _run_command = _components.declare_component("run_command", url="http://localhost:3000")
else :
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "./components/frontend/build")
    _get_host = _components.declare_component("get_host", path=build_dir)
    _manage_settings = _components.declare_component("manage_settings", path=build_dir)
    _get_geometry = _components.declare_component("get_geometry", path=build_dir)
    _recipe_inputs_form = _components.declare_component("recipe_inputs_form", path=build_dir)
    _get_hbjson = _components.declare_component("get_hbjson", path=build_dir)
    _study_progress = _components.declare_component("study_progress", path=build_dir)
    _send_geometry = _components.declare_component("send_geometry", path=build_dir)
    _create_study = _components.declare_component("create_study", path=build_dir)
    _send_hbjson = _components.declare_component("send_hbjson", path=build_dir)
    _auth_user = _components.declare_component("auth_user", path=build_dir)
    _send_results = _components.declare_component("send_results", path=build_dir)
    _select_account = _components.declare_component("select_account", path=build_dir)
    _select_run = _components.declare_component("select_run", path=build_dir)
    _select_study = _components.declare_component( "select_study", path=build_dir)
    _select_recipe = _components.declare_component("select_recipe", path=build_dir)
    _select_project = _components.declare_component("select_project", path=build_dir)
    _select_cloud_artifact = _components.declare_component("select_cloud_artifact", path=build_dir)
    _epw_map = _components.declare_component("epw_map", path=build_dir)
    _read_local_file = _components.declare_component("read_local_file", path=build_dir)
    _run_command = _components.declare_component("run_command", path=build_dir)

def get_host(key='po-get-host'):
    """Create a new instance of "get_host".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    host: 'web' | 'rhino' | 'revit' | 'sketchup'
    """

    get_host = _get_host(
      component='get_host',
      key=key
    )

    return get_host

def manage_settings(key='po-manage-settings', *, settings):
    """Create a new instance of "get_host".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    settings: dict
        A dictionary with the following structure
        
        { 
            "location":{
                        "city": string,
                        "latitude": float,
                        "longitude": float,
                        "time_zone": float,
                        "elevation": integer
                        },
            "units": 'Meters' | 'Millimeters' | 'Feet' | 'Inches' | 'Centimeters',
            "layers": string[],
            "tolerance": float,
            "angle_tolerance": float
        }

    Returns
    -------
    settings: 
        A dictionary with the following structure

        { 
            "location":{
                        "city": string,
                        "latitude": float,
                        "longitude": float,
                        "time_zone": float,
                        "elevation": integer
                        },
            "units": 'Meters' | 'Millimeters' | 'Feet' | 'Inches' | 'Centimeters',
            "layers": string[],
            "tolerance": float,
            "angle_tolerance": float
        }
    """

    manage_settings = _manage_settings(
      component='manage_settings',
      key=key, 
      settings=settings
    )

    return manage_settings

def run_command(key='po-command',
                command='',
                trigger=None,
                prefix='Run_', 
                hide_button=False):

    """Create a new instance of "get_host".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    command: dict or str
        A string that represent the command name to exec. OR

        A dictionary with the following structure
        ```
        {
            'name' : <NAME OF THE COMMAND>
            'param' : <PARAM OF THE COMMAND>
        }
        ```
    trigger: bool
        Trigger automatically the command without clicking. Default is disabled.
    prefix: str
        Prefix of the label
    hide_button: bool
        Show / Hide the button
    """

    run_command = _run_command(
        component='run_command',
        key=key,
        command=command,
        trigger=trigger,
        prefix=prefix, 
        hide_button=hide_button
    )

    return run_command

def get_geometry(
    key: str = 'po-get-geometry', *, 
    label: str = None, 
    use_icon: bool = False,
    options: dict = None,
    mesh_options: dict = None,
    filter: dict = None,
    full_width: bool = False,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None,
):
    """Create a new instance of "get_geometry".

    Parameters
    ----------
    key: str or None
        An optional but important key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
        It is used to identify the preview of the selection.
    label: str or None
        A string that will be displayed on the button. Defaults to "Get Geometry"
    label: bool or None
        Show pollination icon
    options: dictionary or None
        A dictionary to show / hide button options. Defaults each option to visible & unselected.

        {
            "subscribe" : {
                "show": True or False,
                "selected": True or False
            },
            "selection" : {
                "show": True or False,
                "selected": True or False
            },
            "preview" : {
                "show": True or False,
                "selected": True or False
            }
        }

    mesh_options:
        A dictionary to convert geometry to meshes - if CAD plugin supports this feature.
        Use the following schema

        {
            "gridSize" : float,
            "union": bool
        }

        Both attributes are optional.

        'gridSize' to create gridded meshes

        'union' to merge all meshes together

    filter:
        A dictionary to filter the selection of the geometries - if CAD plugin supports this feature.
        Use the following schema

        {
            "layer" : List[str],
            "type": List[str]
        }

        Both attributes are optional.

        'layer' to filter by layers. E.g. ['Layer 02', 'Default'] on Rhino
        
        'type' to filter by object type. E.g. ['point', 'extrusion'] on Rhino

    full_width:
        True to fit the parent width. Default is False.

    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.

    Returns
    -------
    dict
        A dictionary with the following structure

        {
            'geometry': List[dict]
        }

        where
            'geometry': List of ladybug geometries as dictionary
    """
    
    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)

    get_geometry = _get_geometry(
      component='get_geometry',
      key=key, 
      use_icon=use_icon,
      button_label=label, 
      options_config=options,
      mesh_options = mesh_options,
      filter = filter,
      full_width = full_width,
    )

    return get_geometry

def get_hbjson(
    key: str = 'po-get-model', *,
    label: str = None,
    use_icon: bool = True,
    options: Dict = None,
    full_width: bool = False,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None,
):
    """Create a new instance of "get_hbjson".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
        It is used to identify the preview of the selection.
    label: str or None
        A string that will be displayed on the button. Defaults to "Get Geometry"
    options: dictionary or None
        A dictionary to show / hide button options. Defaults each option to visible & unselected.

        {
            "subscribe" : {
                "show": True or False,
                "selected": True or False
            },
            "selection" : {
                "show": True or False,
                "selected": True or False
            },
            "preview" : {
                "show": True or False,
                "selected": True or False
            }
        }

    full_width:
        True to fit the parent width. Default is False.

    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.

    Returns
    -------
    dict
        A dictionary with the following structure

        {
            'hbjson': dict
        }

        where
            'hbjson': hbjson model as dictionary
    """

    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)

    get_hbjson = _get_hbjson(
      component='get_hbjson',
      key=key, 
      button_label=label, 
      use_icon=use_icon,
      options_config=options,
      full_width = full_width
    )

    return get_hbjson

def send_geometry(
    key='po-send-geometry', *, 
    geometry: Union[Dict, list]={}, 
    option='preview', 
    options: dict = None,
    geometry_options: dict = None):

    """Create a new instance of "send_geometry".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    geometry: dictionary
        A single ladybug geometry or an array of ladybug geometries.

        https://www.ladybug.tools/ladybug-display-schema/geometry.html

        https://www.ladybug.tools/ladybug-display-schema/display.html

        Example
        ```
        from pollination_streamlit_io import send_geometry
        
        # pure geometry
        face = {
            "type": "Face3D",
            "boundary": [
                [4, 4, 0],
                [8, 4, 0],
                [8, 8, 0],
                [4, 8, 0]
            ],
            "plane": {
                "type": "Plane",
                "n": [0, 0, 1],
                "o": [0, 0, 0],
                "x": [1, 0, 0]
            }
        }

        # or display geometries 
        display_face = {
            "type": "DisplayFace3D",
            "geometry": {
                "type": "Face3D",
                "boundary": [
                    [0, 0, 0],
                    [4, 0, 0],
                    [4, 4, 0],
                    [0, 4, 0]
                ],
                "plane": {
                    "type": "Plane",
                    "n": [0, 0, 1],
                    "o": [0, 0, 0],
                    "x": [1, 0, 0]
                },
                "holes": [
                    [
                        [1, 1, 0],
                        [1.5, 1, 0],
                        [1.5, 1.5, 0],
                        [1, 1.5, 0]
                    ],
                    [
                        [2, 2, 0],
                        [3, 2, 0],
                        [3, 3, 0],
                        [2, 3, 0]
                    ]
                ]
            },
            "color": {
                "type": "Color",
                "r": 255,
                "g": 0,
                "b": 0,
                "a": 255
            },
            "display_mode": "Surface"
        }

        sent_geometry = send_geometry('send-geometry', 
                                    geometry=[face, display_face],
                                    option='preview',
                                    options={ 'clear': False })
        ```
    option: 'add' | 'preview' | 'clear' | 'subscribe-preview'
        An option that modifies the action to be taken in the host CAD platform.
    options: dictionary or None
        A dictionary to show / hide button options. Defaults to show all.

        {
            'add' = True or False
            'delete' = True or False
            'preview' = True or False
            'clear' = True or False
            'subscribe-preview' = True or False
        }
    geometry_options: dictionary or None
        A dictionary to control translation of geometry from app to CAD plugin.
        Defaults to using the CAD plugin document settings.

        {
            'units' = 'Meters' | 'Millimeters' | 'Feet' | 'Inches' | 'Centimeters',
        }
    Returns
    -------
    """

    send_geometry = _send_geometry(
      component='send_geometry',
      key=key,
      geometry=geometry,
      option=option,
      options_config=options,
      geometry_options=geometry_options
    )

    return send_geometry

def send_hbjson(key='po-send-hbjson', *, 
    hbjson={}, 
    option='preview',
    options: dict = None):

    """Create a new instance of "send_hbjson".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    hbjson: dictionary
        An hbjson model as a dictionary.
    option: 'add' | 'preview' | 'clear' | 'subscribe-preview'
        An option that modifies the action to be taken in the host CAD platform.
    options: dictionary or None
        A dictionary to show / hide button options. Defaults to show all.

        {
            'add', = True or False
            'delete', = True or False
            'preview', = True or False
            'clear', = True or False
            'subscribe-preview' = True or False
        }
    Returns
    -------
    """

    send_hbjson = _send_hbjson(
        component='send_hbjson',
        key=key,
        hbjson=hbjson,
        option=option,
        options_config=options
    )

    return send_hbjson

def send_results(key='po-send-results', *, 
    results={}, 
    option='preview', 
    options=None, 
    geometry_options: dict = None,
    delay=500):
    
    """Create a new instance of "send_results".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    results: dictionary
        VisualizationSet object.

        https://github.com/ladybug-tools/ladybug-display-schema/tree/master/samples/vsf

        Example
        ```
        import json
        from pollination_streamlit_io import send_results

        visualization_set = open('examples/apps/files/vsf.json')

        send_results('send-results', 
                    results=json.load(visualization_set), 
                    options={ 'clear': False, 'delete': False }, 
                    option='preview')
        ```

    option: 'add' | 'delete' | 'preview' | 'clear' | 'subscribe-preview'
        An option that modifies the action to be taken in the host CAD platform.
    options: dictionary or None
        A dictionary to show / hide button options. Defaults to show all.

        {
            'add', = True or False
            'delete', = True or False
            'preview', = True or False
            'clear', = True or False
            'subscribe-preview' = True or False
        }
    geometry_options: dictionary or None
        A dictionary to control translation of geometry from app to CAD plugin.
        Defaults to using the CAD plugin document settings.

        {
            'units' = 'Meters' | 'Millimeters' | 'Feet' | 'Inches' | 'Centimeters',
        }
    delay: int
        Delay of the subscription in milliseconds. Default is 500ms
    Returns
    -------
    """

    send_results = _send_results(
        component='send_results',
        key=key, 
        results=results, 
        option=option, 
        options_config=options, 
        geometry_options=geometry_options,
        delay=delay
    )

    return send_results

def auth_user(key='po-auth-user', api_client: Union[ApiClient, Dict] = None):
    """Create a new instance of "auth_user".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client
        ```
        If Dict it has the following structure
        ```
            {
                '_api_token': '...',
                '_host': '...'
            }
        ```
    
    Returns
    -------
    dict
        A dictionary with the following structure

        {
            'id': string
            'email': string
            'name': string
            'username': string
            'description': string or None
            'picture': string or None
        }
    """
    if isinstance(api_client, ApiClient):
        client = api_client.__dict__
    else:
        client = api_client

    auth_user = _auth_user(
      component='auth_user',
      key=key,
      access_token=client.get("_jwt_token"),
      api_key=client.get("_api_token"),
      base_path=client.get("_host")
    )

    return auth_user

def select_account(
    key='po-select-account',
    api_client: Union[ApiClient, Dict] = None, *,
    default_account_username: str = None,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None,
):
    """Create a new instance of "select_account".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client
        ```
        If Dict it has the following structure
        ```
            {
                '_api_token': '...',
                '_host': '...'
            }
        ```
    default_account_username: str
        default account name, component will select this account as a default state
    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.
    
    Returns
    -------
    dict
        A dictionary with the following structure

        {
            'id': string
            'email': string or None
            'contact_email': string or None
            'name': string
            'username': string or None
            'account_name': string or None
            'description': string or None
            'picture': string or None
            'picture_url': string or None
            'owner': dictionary or None
            'role': string or None
            'member_count': number or None
            'team_count': number or None
        }

        where

            'owner': dictionary with the following structure

            {
              'id': string
              'type': 'org' | 'user'
              'name': string
            }
    """
    if isinstance(api_client, ApiClient):
        client = api_client.__dict__
    else:
        client = api_client

    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)

    select_account = _select_account(
      component='select_account',
      key=key,
      default_account_username=default_account_username,
      access_token=client.get("_jwt_token"),
      api_key=client.get("_api_token"),
      base_path=client.get("_host")
    )

    return select_account

def select_cloud_artifact(
    key='po-select-cloud-artifact',
    api_client: Union[ApiClient, Dict] = None, *,
    project_name: str,
    project_owner: str,
    study_id: str = None,
    file_name_match: str = ".*",
    path: str = None,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None,
):
    """Create a new instance of "select_cloud_artifact".
    It works with cloud artifacts only.

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client
        ```
        If Dict it has the following structure
        ```
            {
                '_api_token': '...',
                '_host': '...'
            }
        ```
    project_name: str
        A project's unique name
    project_owner: str
        The username (user) or account_name (org) of a projects owner
    study_id: str
        If you connect it it reads the study folder instead of the project folder.
        It is optional.
    path: str
        Defining a path where to search for files. It is optional.
    file_name_match: str
        A regular expression to match the file name, e.g. ".*(hbjson$)"
    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.
    
    Returns
    -------
    tuple
        A tuple (name, value, type) where value is binary
    """
    if isinstance(api_client, ApiClient):
        client = api_client.__dict__
    else:
        client = api_client

    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)

    select_cloud_artifact = _select_cloud_artifact(
      component='select_cloud_artifact',
      key=path or key,
      value={ 'key': path } if path else {},
      project_name=project_name,
      project_owner=project_owner,
      study_id=study_id,
      file_name_match=file_name_match,
      access_token=client.get("_jwt_token"),
      api_key=client.get("_api_token"),
      base_path=client.get("_host"),
    )

    if select_cloud_artifact:
        name = select_cloud_artifact['name']
        type = select_cloud_artifact['type']

        if type == 'file':
            value = base64.b64decode(select_cloud_artifact['value'])
        else:
            value = select_cloud_artifact['value']
        
        return name, value, type
    else:
        return None, None, None

def select_project(
    key='po-select-project', 
    api_client: Union[ApiClient, Dict] = None, *,
    project_owner: str = None,
    default_project_id: str = None,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None,
):
    """Create a new instance of "select_project".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client
        ```
        If Dict it has the following structure
        ```
            {
                '_api_token': '...',
                '_host': '...'
            }
        ```
    project_owner: str or None
        username of project owner
    default_project_id: str or None
        default project id
    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.

    Returns
    -------
    dict
        A dictionary with the following structure

            {
                'name': string,
                'description': string or None,
                'public': boolean,
                'id': string,
                'owner': dictionary,
                'permissions': dictionary,
                'slug': string,
                'usage': dictionary,            
            }

            where

                'owner' is a dictionary with the following structure

                    {
                        "id": string,
                        "account_type": string,
                        "name": string,
                        "display_name": string,
                        "description": string or None,
                        "picture_url": string or None
                    }

                'permissions' is a dictionary with the following structure

                    {
                        "admin": boolean,
                        "write": boolean,
                        "read": boolean
                    }

                'usage' is a dictionary with the following structure

                    {
                        "start": string,
                        "end": string,
                        "cpu": int,
                        "memory": int,
                        "succeeded": int,
                        "failed": int,
                        "daily_usage": tuple
                    }
    """

    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)
    
    if isinstance(api_client, ApiClient):
        client = api_client.__dict__
    else:
        client = api_client

    select_project = _select_project(
      component='select_project',
      key=key,
      project_owner=project_owner,
      default_project_id=default_project_id,
      access_token=client.get("_jwt_token"),
      api_key=client.get("_api_token"),
      base_path=client.get("_host")
    )

    return select_project

def select_recipe(
    key='po-select-recipe', 
    api_client: Union[ApiClient, Dict] = None, *, 
    project_name: str = None, 
    project_owner: str = None,
    default_recipe: Dict = None,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None,
):
    """Create a new instance of "select_recipe".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client
        ```
        If Dict it has the following structure
        ```
            {
                '_api_token': '...',
                '_host': '...'
            }
        ```
    project_name: str or None
        project name
    project_owner: str or None
        username of the project owner
    default_recipe: Dict or None
        ProjectRecipeFilter object that will be passed as input to select_recipe
    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.

    Returns
    -------
    dict
        A dictionary with the structure described here:

            https://api.pollination.cloud/docs#/Projects/get_project_recipes

    """
    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)

    if isinstance(api_client, ApiClient):
        client = api_client.__dict__
    else:
        client = api_client

    select_recipe = _select_recipe(
        component='select_recipe',
        key=key,
        project_name=project_name,
        project_owner=project_owner,
        default_recipe=default_recipe,
        access_token=client.get("_jwt_token"),
        api_key=client.get("_api_token"),
        base_path=client.get("_host"))

    return select_recipe

def select_study(
    key='po-select-study', api_client: Union[ApiClient, Dict] = None, *,
    project_name: str = None,
    project_owner: str = None,
    default_study_id: str = None,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None,
):
    """Create a new instance of "select_study".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client
        ```
        If Dict it has the following structure
        ```
            {
                '_api_token': '...',
                '_host': '...'
            }
        ```
    project_name: str or None
        name of project
    project_owner: str or None
        username of project owner
    default_study_id: str or None
        default study id
    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.

    Returns
    -------
    dict
        A dictionary with the structure documented here:

            https://api.pollination.cloud/docs#/Jobs/list_jobs
    """
    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)
    
    if isinstance(api_client, ApiClient):
        client = api_client.__dict__
    else:
        client = api_client

    select_study = _select_study(
        component='select_study',
        key=key,
        project_name=project_name,
        project_owner=project_owner,
        default_study_id=default_study_id,
        access_token=client.get("_jwt_token"),
        api_key=client.get("_api_token"),
        base_path=client.get("_host"))

    return select_study

def select_run(
    key='po-select-run', api_client: Union[ApiClient, Dict] = None, *,
    project_name: str = None,
    project_owner: str = None,
    job_id: str = None,
    default_run_id: str = None,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None
):
    """Create a new instance of "select_run".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client
        ```
        If Dict it has the following structure
        ```
            {
                '_api_token': '...',
                '_host': '...'
            }
        ```
    project_owner: str or None
        username of project owner
    job_id: str or None
        id of study
    default_run_id: str or None
        default run id
    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.
        
    Returns
    -------
    dict
        A dictionary with the sturcture described here:

            https://api.pollination.cloud/docs#/Runs/list_runs
    """

    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)

    if isinstance(api_client, ApiClient):
        client = api_client.__dict__
    else:
        client = api_client

    select_run = _select_run(
        component='select_run',
        key=key,
        project_name=project_name,
        project_owner=project_owner,
        job_id=job_id,
        default_run_id=default_run_id,
        access_token=client.get("_jwt_token"),
        api_key=client.get("_api_token"),
        base_path=client.get("_host"))

    return select_run

def create_study(
    key='po-create-study', 
    api_client: ApiClient = None,
    on_change: Callable = None,
    args: Tuple = None,
    kwargs: Dict = None
):
    """Create a new pollination study.

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient or str
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client()
        ```
    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.
        
    Returns
    -------
        Study object.
    """

    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)

    if isinstance(api_client, ApiClient):
        client = api_client.__dict__
    else:
        client = api_client

    create_study = _create_study(
        component='create_study',
        key=key,
        access_token=client.get("_jwt_token"),
        api_key=client.get("_api_token"),
        base_path=client.get("_host"),
    )

    return Study(create_study,
                 client=api_client)

def recipe_inputs_form(
    key='po-recipe-inputs-form', 
    api_client: ApiClient = None, 
    project_name: str = None,
    project_owner: str = None,
    recipe_filter: Dict = None,
    user_inputs: Dict = {},
    sync_change: bool = False,
    study_name = None,
    show_form = True,
    is_local: bool = False,
    *,
    on_change:  Callable = None,
    args: Tuple = None,
    kwargs: Dict = None
):
    """Create a new pollination study.

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    api_client: ApiClient
        ApiClient is a class returned by get_api_client(), part of the 
        pollination_streamlit package.
        ```
        from pollination_streamlit.selectors import get_api_client
        ...
        api_client = get_api_client()
        ```
    project_name: str
        Unique name representing a project
    project_owner: str
        Unique name representing the project's owner
    recipe_filter: Dict
        Dictionary representing a pollination recipe filter, use select_recipe
    user_inputs: Dict
        Dictionary representing user values.

        ## Common input (not file type)

            <NAME>: <VALUE>

            Example
            ```
            'north': 100
            ```
            where 'north' is the name of the recipe input.


        ## File input

            <NAME>: [<ABSOLUTE OR RELATIVE SOURCE FILE PATH>, <OUTPUT NAME>]

            Example
            ```
            'context-mesh': ['./data/analysis_mesh.json', 'context_mesh.json']
            ```
            where 'context-mesh' is the name of the input; 
            the first item of the list is the relative or absolute path of the source file; 
            the second item of the list is the name of the output file.

        So user_inputs dictionary should be something similar
        ```
        {
            'north': 100,
            'context-mesh': ['./data/analysis_mesh.json', 'context_mesh.json']
        }
        ```

    sync_change: bool
        If user_inputs are available and sync_change is True it will Submit the form with any user_inputs change.
    is_local: bool
        True to select Local run by default.
    study_name: str
        Default study name to use.
    show_form: bool
        False to hide the form. Default is True.
    on_change: Callable or None
        An optional on_change function that will be called when hbjson input
        is changed.
    args: Tuple or None
        An optional tuple of positional arguments that will be passed to the
        on_change function.
    kwargs: dictionary or None
        An optional dictionary of kwargs that will be passed to the on_change
        function.
        
    Returns
    -------
        Study object.
    """
    if on_change is not None:
        args = args or []
        kwargs = kwargs or {}
        register_callback(key, on_change, *args, **kwargs)

    if isinstance(api_client, ApiClient):
        client = api_client.__dict__

    if user_inputs:
        _apply_mapping(user_inputs)

    recipe_inputs_form = _recipe_inputs_form(
        component='recipe_inputs_form',
        key=f'{key}-{recipe_filter.get("name")}',
        access_token=client.get("_jwt_token"),
        api_key=client.get("_api_token"),
        base_path=client.get("_host"),
        project_owner=project_owner,
        project_name=project_name,
        recipe_filter=recipe_filter,
        user_inputs=user_inputs or {},
        trigger_inputs=user_inputs if (sync_change and user_inputs) else None,
        is_local=is_local,
        study_name=study_name,
        show_form=show_form)

    return Study(recipe_inputs_form,
                 client=api_client)

"""
    Study class
"""
class Study(object):
    """Pollination streamlit study. Use create_study and recipe_inputs_form to get it

    Args:
        info: data generated by create_study and recipe_inputs_form
        kwargs: An optional dictionary of kwargs

    Properties:
        * accountName
        * projectName
        * studyId
        * run
        * isLocal
        * refreshKey
        * client
        * progress
        * status
    """
    def __init__(self, info, **kwargs) -> None:
        self.refreshKey = None
        self.progress = 0
        self.status = None

        self.__dict__.update(info or {})
        self.__dict__.update(kwargs)

    @classmethod
    def from_dict(cls, data, api_client):
        """Create a Study from dictionary.

        Parameters
        ----------
            data: dict
                A python dictionary with the following info

            * accountName
            * projectName
            * studyId
            * run
            * isLocal
            * refreshKey
            * client

            api_client: ApiClient or str
                ApiClient is a class returned by get_api_client(), part of the 
                pollination_streamlit package.

        """
        return cls(data, client=api_client)

    def progress_report(
        self,
        show_output=False,
        refresh_interval=None,
        show_result=False,
        color=None,
        show_status_label=False
    ): 
        """Show progress report of the study

        Parameters
        ----------
        show_output: boolean
            Indicate if it want to see output.  
        show_result: boolean
            Set it to True if you want to rendering directly CAD results without clicking.
        refresh_interval: float
            Interval in millisecond to fetch a local run. Default is 5000. Minimum is 200.

            Cloud studies use a static refresh of 5000ms.
        color: str
            HEX color of the status bar
        show_status_label: str
            Show or hide status label

        Returns
        -------
        tuple
            Click on a file card returns a tuple (name, value, type) where value is binary
            
            Click on a folder card returns a tuple (name, value, type) where value is folder path on cloud
        """
        if not self or not self.refreshKey: return [None] * 3

        study_progress = _study_progress(
            component='study_progress',
            key=f'po-progress-{self.refreshKey}' if self.refreshKey else datetime.datetime.now(),
            project_name=self.projectName,
            project_owner=self.accountName,
            run=self.run,
            color=color,
            is_local=self.isLocal,
            show_status_label=show_status_label,
            refresh_interval=refresh_interval,
            show_output=show_output,
            show_result=show_result,
            access_token=self.client.__dict__.get("_jwt_token"),
            api_key=self.client.__dict__.get("_api_token"),
            base_path=self.client.__dict__.get("_host"))
        
        if study_progress and study_progress.get('progress'):
            self.progress = study_progress.get('progress')

        if study_progress and study_progress.get('status'):
            self.status = study_progress.get('status')

        if study_progress and study_progress.get('data'):
            data = study_progress.get('data')
            if not data: return None, None, None

            name = data['name']
            type = data['type']

            if type == 'file':
                value = base64.b64decode(data['value'])
            else:
                value = data['value']
            return name, value, type
        
        return [None] * 3

    def download_artifact(self, path: str) -> Union[bytes, None]:
        """Download artifact by path

        Parameters
        ----------
        path: str
            Relative path where the file is. E.g.
            ```
            path = 'results/direct_sun_hours/sun-up-hours.txt'
            ```
        Returns
        -------
        bytes
            File in bytes format. If file is a text you can get the string using
            ```
            text = my_bytes.decode('utf-8')
            ```
        """
        content = None

        if not self or self.progress != 100: return content

        if self.isLocal:
            if not self.run.get('studyName'): return

            job_name = re.sub('[^a-zA-Z0-9]+', '', self.run.get('studyName'))
            target = Path(self.studyId, job_name, path).as_posix()
            
            # workaround containers
            base64_code = _read_local_file(key=path, 
                                   component='read_local_file',
                                   file_path=target)
            if base64_code:
                data = base64_code.encode()
                content = base64.b64decode(data)
        else:
            jobs_api = JobsAPI(client=self.client)
            complete_path = Path('runs', self.run.get('id'), 'workspace', path).as_posix()

            byte_io = jobs_api.get_job_artifact(self.accountName, 
                                                self.projectName,
                                                self.studyId, 
                                                complete_path)
            if byte_io:
                content = byte_io.getvalue()

        return content

def epw_map(
    key='po-epw-map',
    show_legend: bool = True, 
    latitude: float = 44, 
    longitude: float = -35,
    style: dict = {},
    static_image_style: dict = None,
    widget_style: dict = {}):

    """Create a new instance of "send_geometry".

    Parameters
    ----------
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    show_legend: bool
        False to hide the legend.
    latitude: float
        Initial latitude.
    longitude: flaot
        Initial longitude.
    style: dictionary
        Style of the main container. Use JSX sintax for CSS
        Example
        ```
        {
            'borderRadius': '5px solid black'
        }
        ```

    static_image_style: dictionary
        Static images to use with Leaflet. There are many samples at this link:
        https://leaflet-extras.github.io/leaflet-providers/preview/
        Example
        ```
        {
            'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            'maxZoom': 19,
            'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }
        ```

    widget_style: dictionary
        Style of the widget containers. Use JSX sintax for CSS
        Example
        ```
        {
            'backgroundColor': 'rgba(255, 255, 255, 0.9)',
            'color': 'black',
            'border': '2px solid rgba(125, 125, 125, 0.5)'
        }
        ```

    Returns
    -------
    dict
        Weather file information
        Example
        ```
        {
            'id':'619890'
            'station':'Plaine Corail'
            'source':'ISD-TMYx'
            'lat':-19.75
            'lon':63.37
            'link':'http://climate.onebuilding.org/WMO_Region_1_Africa/MUS_Mauritius/MUS_RO_Plaine.Corail.619890_TMYx.zip'
            'host':'onebuilding'
            'color':'#fdb462'
        }
        ```

    """

    epw_map = _epw_map(
      component='epw_map',
      key=key,
      show_legend=show_legend,
      latitude=latitude,
      longitude=longitude,
      style=style,
      static_image_style=static_image_style,
      widget_style=widget_style,
    )

    return epw_map