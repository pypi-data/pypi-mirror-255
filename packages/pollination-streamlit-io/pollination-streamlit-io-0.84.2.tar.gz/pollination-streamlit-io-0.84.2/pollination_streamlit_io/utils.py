"""Utils to make the interface user-friendly
"""

import base64
from pathlib import Path
from typing import Dict


def _get_base64_string(path: Path) -> str:
    try:
        return base64.b64encode(path.read_bytes()).decode('utf-8')
    except Exception as e:
        print(e)
        return

def _apply_mapping(dictionary: dict) -> Dict:
    """ Apply the mapping for frontend input

        Usage
        ```
            my_input = {
                'north': 100,
                'wea': ['C:/ladybug/ITA_Campobasso.162520_IGD/ITA_Campobasso.162520_IGDG.wea', 'weather.wea']
            }

            _apply_mapping(my_input)
        ```
    
    """
    for k, v in dictionary.items():
        if isinstance(v, list):
            source_path, output_name = v
            base64_str = _get_base64_string(Path(source_path))
            if not base64_str:
                dictionary[k] = {}
            else:
                dictionary[k] = { 'value' : {
                        'base64_string': base64_str,
                        'file_name': output_name
                    }
                }
        else:
            dictionary[k] = {
                'value': v
            }