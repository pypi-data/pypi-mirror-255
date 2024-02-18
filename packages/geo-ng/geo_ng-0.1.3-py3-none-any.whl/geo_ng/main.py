import importlib.resources
import json


def load_json_file(json_file):
    with importlib.resources.open_text("data", json_file) as file:
        data = json.load(file)
    return data


states_data = load_json_file('states.json')
lgas_data = load_json_file('lgas.json')
towns_data = load_json_file('towns.json')


def get_states():
    return {"name": "all states", "items": states_data}


def get_states_by_region(region_code):
    regions = ['NE', 'NC', 'NW', 'SS', 'SW', 'SE']  # shortcode for the 6 geopolitical zones
    if region_code not in regions:
        return {"error": "incorrect region"}
    filtered = [state for state in states_data if state["region"]['code'] == region_code]
    return {"name": "states by region", "count": len(filtered), "items": filtered}


def get_lgas():
    return {"name": "all LGAs", "count": len(lgas_data), "items": lgas_data}


def get_lgas_by_state(state_code):
    filtered = [lga for lga in lgas_data if lga["state"] == state_code]
    return {"name": "LGAs by state", "count": len(filtered), "items": filtered}


def get_towns_by_lga(lga_code):
    filtered = [town for town in towns_data if town["lga"] == lga_code]
    return {"name": "Towns by lga", "count": len(filtered), "items": filtered}
