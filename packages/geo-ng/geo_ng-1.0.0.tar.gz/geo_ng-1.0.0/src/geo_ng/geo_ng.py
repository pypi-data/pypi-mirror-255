from importlib.resources import files
import json


def load_file(json_file):
    data = files("geo_ng.data").joinpath(json_file).read_text()
    return json.loads(data)


states_data = load_file('states.json')
lgas_data = load_file('lgas.json')
towns_data = load_file('towns.json')


def get_states():
    return {"name": "all states", "items": states_data}


def get_states_by_region(region_code):
    regions = ['NE', 'NC', 'NW', 'SS', 'SW', 'SE']  # shortcode for the 6 geopolitical zones
    if region_code not in regions:
        return {"error": "incorrect region"}
    filtered = [state for state in states_data if state["region"]['code'] == region_code]
    return {"name": "states by region", "count": len(filtered), "items": filtered}


def get_lgas():
    return {"name": "all LGAs", "count": len(lgas_data),  "items": lgas_data}


def get_lgas_by_state(state_code):
    filtered = [lga for lga in lgas_data if lga["state"] == state_code]
    find_state = next((item for item in states_data if item["code"] == state_code), False)
    return {"name": "LGAs by state", "state": find_state['name'], "count": len(filtered), "items": filtered}


def get_towns_by_lga(lga_code):
    filtered = [town for town in towns_data if town["lga"] == lga_code]
    find_lga = next((item for item in lgas_data if item["code"] == lga_code), False)
    print(find_lga)
    return {"name": "Towns by lga", "lga": find_lga['name'], "count": len(filtered), "items": filtered}
