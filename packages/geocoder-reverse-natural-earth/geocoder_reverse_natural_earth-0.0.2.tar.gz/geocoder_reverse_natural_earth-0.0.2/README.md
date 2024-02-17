# geocoder_reverse_natural_earth

Reverse lookup of locations using Natural-Earths administrative boundary shp-database. This allows
a simple lookup from geo-location in latitude/longitude to a countries ISO2 code.


## License

The python code in this package is licensed under the LGPL >= 2.1, see LICENSE.

The Natural-Earth database included as zip file is in public domain,
see https://www.naturalearthdata.com/about/terms-of-use/ .

![NaturalEarth-logo](NEV-Logo-color.png "Natural Earth Logo")

## Installation

The following will install geocoder_reverse_natural_earth and all dependencies.

`python -m pip install geocoder_reverse_natural_earth`

or for the latest development version:

`python -m pip install 'geocoder_reverse_natural_earth@git+https://github.com/metno/geocoder_reverse_natural_earth.git'`



## Usage
geocoder_reverse_natural_earth is small helper to identify country codes for obs networks that don't mention the
countrycode of a station in their location data
```python
from geocoder_reverse_natural_earth import (
    Geocoder_Reverse_NE,
    Geocoder_Reverse_Exception,
)
geo = Geocoder_Reverse_NE()
print(geo.lookup(60, 10)["ISO_A2_EH"])
lat = 78.2361926
lon = 15.3692614
try:
    geo.lookup(lat, lon)
except Geocoder_Reverse_Exception as grex:
    dummy = geo.lookup_nearest(lat, lon)
    if dummy is None:
        print(f"error: {lat},{lon}")
    else:
        print(dummy["ISO_A2_EH"])



```
