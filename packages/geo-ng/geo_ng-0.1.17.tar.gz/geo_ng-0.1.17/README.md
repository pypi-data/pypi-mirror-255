# geo-ng

An installable python package that provides geographical information about States, Local Govenment Areas and towns in Nigeria


### Installation
`pip install geo-ng`


### Usage
```py
# Get all existing states
from geo_ng import get_states
get_states()


# Get states by region
from geo_ng import get_states_by_region
get_states_by_region(region_code)


# Get all existing local govenment areas
from geo_ng import get_lgas
get_lgas()


# Get local govenment by state
from geo_ng import get_lgas_by_state
get_lgas_by_state(state_code)

# Get towns by local govenment area
from geo_ng import get_towns_by_lga
get_towns_by_lga(lga_code)
```