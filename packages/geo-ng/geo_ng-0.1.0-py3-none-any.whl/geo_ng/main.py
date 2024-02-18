import json

# Opening JSON file
states = open('src/geo_ng/data/states.json')
lgas = open('src/geo_ng/data/lgas.json')
towns = open('src/geo_ng/data/towns.json')

states_data = json.load(states)
lgas_data = json.load(lgas)
towns_data = json.load(towns)


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
    return {"name": "LGAs by state", "count": len(filtered), "items": filtered}


def get_towns_by_lga(lga_code):
    filtered = [town for town in towns_data if town["lga"] == lga_code]
    return {"name": "Towns by lga", "count": len(filtered), "items": filtered}
