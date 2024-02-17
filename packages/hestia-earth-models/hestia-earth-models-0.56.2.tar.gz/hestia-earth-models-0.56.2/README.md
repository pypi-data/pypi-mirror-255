# Hestia Engine Models

[![Pipeline Status](https://gitlab.com/hestia-earth/hestia-engine-models/badges/master/pipeline.svg)](https://gitlab.com/hestia-earth/hestia-engine-models/commits/master)
[![Coverage Report](https://gitlab.com/hestia-earth/hestia-engine-models/badges/master/coverage.svg)](https://gitlab.com/hestia-earth/hestia-engine-models/commits/master)

Hestia's set of models for running calculations or retrieving data using external datasets and internal lookups.

## Documentation

Documentation for every model can be found in the [Hestia API Documentation](https://hestia.earth/docs/#hestia-calculation-models).

## Install

1. Install python `3` (we recommend using python `3.6` minimum)
2. Install the module:
```bash
pip install hestia_earth.models
```
3. Set the following environment variables:
```
API_URL=https://api.hestia.earth
WEB_URL=https://hestia.earth
```

### Usage

```python
from hestia_earth.models.pooreNemecek2018 import run

# cycle is a JSONLD node Cycle
run('no3ToGroundwaterSoilFlux', cycle_data)
```

### Using Spatial Models

We have models that can gap-fill geographical information on a `Site`.
If you want to use thse models:
1. Install the library: `pip install hestia_earth.earth_engine`
2. Follow the [Getting Started instructions](https://gitlab.com/hestia-earth/hestia-earth-engine#getting-started).

### Using Ecoinvent Model

ecoinvent is a consistent, transparent, and well validated life cycle inventory database.
We use ecoinvent data to ascertain the environmental impacts of activities that occur outside of our system boundary, for example data on the environmental impacts of extracting oil and producing diesel, or the impacts of manufacturing plastics.
To include these data in your environmental impact assessments using Hestia, you must own a suitable [ecoinvent license](https://ecoinvent.org/offerings/licences/).

Please contact us at community@hestia.earth for instructions to download the required file to run the model.
Once downloaded, copy the file in the _hestia_earth/models/data/ecoinventV3_ folder.
Thank you!
