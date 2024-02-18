import logging
import json
import os
from fastapi.testclient import TestClient
import requests
from src.pythia_client.client import APIClient

logging.basicConfig(
    filename="test.log",
    filemode="w",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s: %(message)s",
)

URL = os.getenv("HAYSTACK_API_URL", "http://localhost:8000/")
SECRET_MASTER_API_KEY = os.getenv("SECRET_MASTER_API_KEY")

client = APIClient(url=URL, api_key=SECRET_MASTER_API_KEY)


def test_index_files_client():
    file_paths = [
        "test/samples/sample1.pdf",
        "test/samples/sample2.pdf",
    ]
    meta = [
        {"meta1": "value1", "source_test": "pytest_client_api"},
        {"meta2": "value2", "source_test": "pytest_client_api"},
    ]
    indexation_mode = "unstructured"
    response = client.index_files(
        files=file_paths, meta=meta, indexation_mode=indexation_mode
    )
    assert response is not None
    assert response.Writter.documents_written >= 3


def test_index_files_from_bytes_client():
    file_paths = [
        "test/samples/sample3.pdf",
    ]
    file_names = ["sample3.pdf"]
    tuple_files = [
        (file_name, open(file_path, "rb"))
        for file_name, file_path in zip(file_names, file_paths)
    ]
    meta = [
        {"meta3": "value3", "source_test": "pytest_client_api"},
    ]
    indexation_mode = "unstructured"
    response = client.index_files(
        files=tuple_files, meta=meta, indexation_mode=indexation_mode
    )
    assert response is not None
    assert response.Writter.documents_written >= 2


def test_list_docs_client():
    filters = {
        "operator": "AND",
        "conditions": [
            {
                "field": "meta.source_test",
                "operator": "==",
                "value": "pytest_client_api",
            }
        ],
    }
    response = client.list_docs(filters=filters)

    assert response is not None
    assert len(response) >= 5
    assert len(response) < 20
    assert len(response[0].content) > 20
    assert response[0].meta["source_test"] == "pytest_client_api"
    assert response[0].meta["filename"] == response[0].meta["s3_key"]

def test_query_client():
    response = client.query(query="Hey how are you ?")
    assert response is not None
    assert len(response.AnswerBuilder.answers[0].data) > 20

def test_get_doc_url_client():
    filters = {
        "operator": "AND",
        "conditions": [
            {
                "field": "meta.source_test",
                "operator": "==",
                "value": "pytest_client_api",
            }
        ],
    }
    doc_in_docstore = client.list_docs(filters=filters)
    s3_key = doc_in_docstore[0].meta["s3_key"]
    page = 1
    response = client.get_doc_url(filename=s3_key, page=page)
    assert response is not None
    assert len(response.url) >= 100
    aws_s3_response = requests.get(response.url)
    assert aws_s3_response.status_code == 200


def test_remove_docs_client():
    filters = {
        "operator": "AND",
        "conditions": [
            {
                "field": "meta.source_test",
                "operator": "==",
                "value": "pytest_client_api",
            }
        ],
    }
    response = client.remove_docs(filters=filters)

    assert response is not None
    assert response.n_deleted_docstore >= 5
    assert response.n_deleted_s3 == 3
    assert len(response.deleted_s3_keys) == 3


def test_extract_json_data_client():
    email = """Bonjour, Je vous écris car j'ai un problème avec la commande FR082475927. Deux DECT Intercorm ont un défaut et ne s'allument pas, pouvez-vous m'aider ? Bonne journée, Cordialement,Entreprise MEDICOMPANY SAS"""

    response = client.extract_json_data(text_content=email)

    assert len(response.OutputValidator.valid_replies) == 1

    formatted_json = response.OutputValidator.valid_replies[0].model_dump()

    assert response is not None
    assert len(formatted_json["company_or_client_name"]) > 5
    assert formatted_json["ticket_category"] == "Dead on arrival"
    assert len(formatted_json["ticket_category"]) > 5
    assert formatted_json["command_number"][0:2] == "FR"
