# pythia-client
This is the client make it easier to interact with our internal Pythia API.  
This is still a work in progress 
## Usage
* Create a connection with client object
```python
from pythia_client.client import APIClient
client = APIClient(url="http://localhost:8000", api_key="api-key")
```
* Query the knowledge base (ask a question)
```python
filters = {
    "operator": "AND",
    "conditions": [
    {
        "field": "meta.source",
        "operator": "==",
        "value": "Salesforce",
        },
    ],
}
query_response = client.query("Hey how are you", filters=filters)
query_response.model_dump()
```

* Index new files in the knowledge base
```python
index_response = client.index_files(["path/to/file.pdf"], meta=[{"source": "Salesforce"}], indexation_mode="pypdf")
index_response.model_dump()
# OR
index_response = client.index_files([("file.pdf", file)], meta=[{"source": "Salesforce"}], indexation_mode="pypdf")
index_response.model_dump()
```

* List documents in the knowledge base (based on filters)
```python
filters = {
    "operator": "AND",
    "conditions": [
    {
        "field": "meta.source",
        "operator": "==",
        "value": "Salesforce",
        },
    ],
}
list_response = client.list_docs(filters=filters)
list_response.model_dump()
```

* Remove documents from the knowledge base
```python
filters = {
    "operator": "AND",
    "conditions": [
    {
        "field": "meta.source",
        "operator": "==",
        "value": "Salesforce",
        },
    ],
}
remove_response = client.remove_docs(filters=filters)
remove_response.model_dump()
```

* Get a presigned S3 url to the original document
```python
get_doc_response = client.get_doc_url("s3fd_sample.pdf", page=2)
s3_url = get_doc_response.url
```

* Extract JSON data from unstructured test.  
*Currently used to showcase the Email2Case feature.*
```python
extract_response = client.extract_json_data("Hello I want to modify the delivery date of order FR73681920")
extract_response.model_dump()
```