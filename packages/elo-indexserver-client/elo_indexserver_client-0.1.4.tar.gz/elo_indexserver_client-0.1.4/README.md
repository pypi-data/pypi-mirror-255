# ELO indexserver client

Developed by [Treskon GmbH](https://treskon.at/) published on PyPI: https://pypi.org/project/elo-indexserver-client/

A client library for accessing Indexserver component of [ELO Digital Office GmbH](https://www.elo.com/de-at.html) via
REST API.

**Under no circumstances should you use store any sensitive information such as passwords, customer names, ... in this
repository.**

## Installation

```bash
pip install elo-indexserver-client
```

## Usage

First, init the Service with the baseurl, user and password of the Indexserver REST API.

```python
from eloservice.elo_service import EloService

rest_baseurl = "http://localhost::6056/ix-Archive/rest/"
rest_user = "elo"
rest_password = "elo"
elo_service = EloService(url=rest_baseurl, user=rest_user, password=rest_password)
```

Then you can use the service to access the Index server REST API.
Here are often used methods:

```python
# Create Folder 
folder_id = elo_service.create_folder(path="¶Foodplaces", separator="¶")
# upload_file
file_id = elo_service.upload_file(sord_id=folder_id, file_path="test.jpg", file_name="ichiran_ramen.jpg")
# overwrite_mask_fields
elo_service.overwrite_mask_fields(sord_id=file_id, mask_name="Images", metadata={
    "LATITUDE": "35.73258119685775",
    "LONGITUDE": "139.71412884357233",
    "ITEMDOCDATE": "2023-12-26"
})
# search
search_result = elo_service.search(search_mask_fields={"LATITUDE": "35.73258119685775"}, max_results=1)
print(f"sordID of the found file: {search_result[0]}")
```

For more methods see the python docstrings in the code.

## Development

Install poetry: https://python-poetry.org/docs/#installation

```bash
# Install dependencies
poetry install

# activate shell
poetry shell

# Run tests
python -m unittest discover test
```

## Building / publishing this package

This project uses [Poetry](https://python-poetry.org/) to manage dependencies and packaging. Here are the basics:

1. Update the metadata in pyproject.toml (e.g. authors, version)
1. If you're using a private repository, configure it with Poetry
    1. `poetry config repositories.<your-repository-name> <url-to-your-repository>`
    1. `poetry config http-basic.<your-repository-name> <username> <password>`
1. Publish the client with `poetry publish --build -r <your-repository-name>` or, if for public PyPI,
   just `poetry publish --build`

If you want to install this client into another project without publishing it (e.g. for development) then:

1. If that project **is using Poetry**, you can simply do `poetry add <path-to-this-client>` from that project
1. If that project is not using Poetry:
    1. Build a wheel with `poetry build -f wheel`
    1. Install that wheel from the other project `pip install <path-to-wheel>`


## License

Copyright [2024] [Treskon GmbH]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.