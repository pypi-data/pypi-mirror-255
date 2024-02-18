# Standard imports
import os
from typing import Dict, Union, Optional, Tuple

# Third-party imports
import requests
from typeguard import typechecked


### Helper functions ###


def _create_headers(verbose: Optional[bool] = False) -> Dict[str, str]:
    headers = {
        "X-API-Key": os.getenv("TWINLAB_API_KEY"),
        "X-Language": "python",
    }
    verbose_str = "true" if verbose else "false"
    headers["X-Verbose"] = verbose_str
    return headers


def _get_response_body(response: requests.Response) -> Union[dict, str]:
    # TODO: Use attribute of response to check if json/text
    try:
        return response.json()
    except:
        return response.text


###  ###

### API ###


@typechecked
def get_user(verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/user"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def get_versions(verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/versions"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def generate_upload_url(dataset_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/upload_url/{dataset_id}"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def process_uploaded_dataset(dataset_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/datasets/{dataset_id}"
    headers = _create_headers(verbose=verbose)
    response = requests.post(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def upload_dataset(
    dataset_id: str, data_csv: str, verbose: Optional[bool] = False
) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/datasets/{dataset_id}"
    headers = _create_headers(verbose=verbose)
    request_body = {"dataset": data_csv}
    response = requests.put(url, headers=headers, json=request_body)
    body = _get_response_body(response)
    return body


@typechecked
def list_datasets(verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/datasets"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def view_dataset(dataset_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/datasets/{dataset_id}"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def summarise_dataset(dataset_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/datasets/{dataset_id}/summarise"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def delete_dataset(dataset_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/datasets/{dataset_id}"
    headers = _create_headers(verbose=verbose)
    response = requests.delete(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def train_model(
    model_id: str, parameters_json: str, processor: str, verbose: Optional[bool] = False
) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/models/{model_id}"
    headers = _create_headers(verbose=verbose)
    headers["X-Processor"] = processor
    request_body = {
        # TODO: Add dataset_id and dataset_std_id as keys?
        # TODO: Split this into setup/train_params as in twinLab?
        "parameters": parameters_json,
    }
    response = requests.put(url, headers=headers, json=request_body)
    body = _get_response_body(response)
    return body


@typechecked
def list_models(verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/models"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def get_status_model(model_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/models/{model_id}"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def view_model(model_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/models/{model_id}/view"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def summarise_model(model_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/models/{model_id}/summarise"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    body = _get_response_body(response)
    return body


@typechecked
def delete_model(model_id: str, verbose: Optional[bool] = False) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/models/{model_id}"
    headers = _create_headers(verbose=verbose)
    response = requests.delete(url, headers=headers)
    body = _get_response_body(response)
    return body


# Synchronous endpoints


def _use_request_body(
    data_csv: Optional[str] = None, data_std_csv: Optional[str] = None, **kwargs
) -> dict:
    request_body = {"kwargs": kwargs}
    if data_csv is not None:
        request_body["dataset"] = data_csv
    if data_std_csv is not None:
        request_body["dataset_std"] = data_std_csv
    return request_body


@typechecked
def use_model(
    model_id: str,
    method: str,
    data_csv: Optional[str] = None,
    data_std_csv: Optional[str] = None,
    processor: Optional[str] = "cpu",
    verbose: Optional[bool] = False,
    **kwargs,
) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/models/{model_id}/{method}"
    headers = _create_headers(verbose=verbose)
    headers["X-Processor"] = processor
    request_body = _use_request_body(data_csv, data_std_csv, **kwargs)
    response = requests.post(url, headers=headers, json=request_body)
    body = _get_response_body(response)
    return body


# Asynchronous endpoints


@typechecked
def use_request_model(
    model_id: str,
    method: str,
    data_csv: Optional[str] = None,
    data_std_csv: Optional[str] = None,
    processor: Optional[str] = "cpu",
    verbose: Optional[bool] = False,
    **kwargs,
) -> dict:
    url = f"{os.getenv('TWINLAB_URL')}/models/{model_id}/async/{method}"
    headers = _create_headers(verbose=verbose)
    headers["X-Processor"] = processor
    request_body = _use_request_body(data_csv, data_std_csv, **kwargs)
    response = requests.post(url, headers=headers, json=request_body)
    body = _get_response_body(response)
    return body


@typechecked
def use_response_model(
    model_id: str,
    method: str,
    process_id: str,
    verbose: Optional[bool] = False,
) -> Tuple[int, dict]:
    url = f"{os.getenv('TWINLAB_URL')}/models/{model_id}/async/{method}/{process_id}"
    headers = _create_headers(verbose=verbose)
    response = requests.get(url, headers=headers)
    status = response.status_code
    body = _get_response_body(response)
    return status, body


### ###
