# SOL Python ORM Library

## Installation
```
pip install sol-orm-lib
```

## Example usage
```python
from sol_orm_lib.models import *
from sol_orm_lib.sol_orm import SolORM

# Instantiate SolORM object
db = SolORM("https://db-api.sol.idener.es")

# Create an object 
mw = MeasuredWeather(
    rad_ar=27.2,
    temp_ar=39,
    wind_ar=12,
    timestamp=current_milli_time(),
)

# Add it to the DB
response = db.add_entity(mw)
print(response)
```

### Local ORM
```python
from sol_orm_lib.models import *
from sol_orm_lib.sol_local_orm import SolLocalORM

db = SolLocalORM(host="100.91.35.146", port=3306, db="bcm", user="bcm", password="bcm", debug=True)

ent = StorageStatusTAC(
    k=1,
    n=2,
    storageActual=3,
    storageActualKwh=4,
    storageInverterRealised=5,
    storageMax=6
)

db.add_entity(ent)
result = db.get_last_entity(StorageStatusTAC)
print(result)
```

## Release process
To release a new version of the package, update the version number in the `pyproject.toml` file and publish a release with the same tag. The CI will build and publish the package to PyPI.
