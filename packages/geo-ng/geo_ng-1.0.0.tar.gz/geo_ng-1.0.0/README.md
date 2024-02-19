# geo-ng

A python package that provides geographical information about States, Local Govenment Areas and towns in Nigeria


### Installation
`pip install geo-ng`

### Upgrade
`pip install geo-ng --upgrade`

### Usage
```py
# import package
from geo_ng import geo_ng


# Get all existing states
geo_ng.get_states()


# Get states by region
geo_ng.get_states_by_region(region_code)


# Get all existing local govenment areas
geo_ng.get_lgas()


# Get local govenment by state
geo_ng.get_lgas_by_state(state_code)


# Get towns by local govenment area
geo_ng.get_towns_by_lga(lga_code)
```