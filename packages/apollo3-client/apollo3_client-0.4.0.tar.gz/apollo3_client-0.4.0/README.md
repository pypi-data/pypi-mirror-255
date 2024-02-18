# apollo3-client (WIP)
Python library for accessing the [Apollo3](https://github.com/GMOD/Apollo3) API.

## Installation

The package can be installed with `pip`:

```bash
pip install apollo3-client
```

The package can be installed with `poetry`:

```bash
poetry add apollo3-client
```

### Requirements

- Python 3.8+

## Quick Start

To use this library, you must have apollo3 api uri. We can specify it as a string when creating the `apollo3.Client` object. This is a basic example of the creating the client.

Note: username and password is required by apollo for root authentication (Implementation in progress).
If we don't pass username and password then the client will use guest login to get the jwt token

```python
from apollo3 import Apollo3Client

client = Apollo3Client(api_url="http://localhost:3999")
assemblies = client.assemblies_obj()

for assembly in assemblies:
    changes = client.changes_obj(assembly_id=assembly.id)
    for change in changes:
        feature = client.feature(feature_id=change.feature_id)
        print(feature)

```

## Endpoints
| Apollo3 Endpoint | Function                                      |
|------------------|-----------------------------------------------|
| /assemblies            | client.assemblies() or client.assemblies_obj() |
| /changes           | client.changes() or client.changes_obj()      |
| /features        | client.feature()                              |

## Contributing

To set up a development environment, first ensure you have [poetry 1.5+ installed](https://python-poetry.org/docs/#installation) and run:

```bash
poetry install  # install and update dependencies in your environment, the first time
```

Configure the APOLLO3_API_URL in [client.py](./apollo3/client.py)

You can run tests locally using:
```bash
poetry run pytest
```
