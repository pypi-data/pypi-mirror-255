# Standard imports
from pprint import pprint
from typing import Optional
import os

# Third-party imports
from typeguard import typechecked

# Project imports
from . import api
from . import utils


@typechecked
def set_api_key(api_key: str, verbose: Optional[bool] = False) -> None:
    """
    # Set API key

    Set the user API key for their `twinLab` cloud account.

    ## Arguments:

    - `api_key`: `str`. API key for the `twinLab` cloud.

    ## Example:

    ```python
    import twinlab as tl

    tl.set_api_key("12345")
    ```
    """
    os.environ["TWINLAB_API_KEY"] = api_key
    if verbose:
        print("API key: {}".format(api_key))


@typechecked
def set_server_url(url: str, verbose: Optional[bool] = False) -> None:
    """
    # Set server URL

    Set the URL from which `twinLab` is being served from.

    ## Arguments:

    - `url`: `str`. URL for the `twinLab` cloud.

    ## Example:

    ```python
    import twinlab as tl

    tl.set_url("https://twinlab.digilab.co.uk")
    ```
    """
    os.environ["TWINLAB_URL"] = url
    if verbose:
        print("Server URL: {}".format(url))


@typechecked
def get_server_url(verbose: Optional[bool] = False) -> str:
    """
    # Get the server URL

    Fetch the URL from which `twinLab` is being served from.

    ## Returns:

    - `str` containing the server URL.

    ## Example:

    ```python
    import twinlab as tl

    tl.get_server_url()
    ```
    """
    server_url = os.getenv("TWINLAB_URL")
    if verbose:
        print("Server URL: {}".format(server_url))
    return server_url


@typechecked
def get_api_key(verbose: Optional[bool] = False) -> str:
    """
    # Get the user API key

    Get a user API key for their`twinLab` cloud account.

    ## Returns:

    - `str` containing the server API key.

    ## Example:

    ```python
    import twinlab as tl

    tl.get_api_key()
    ```
    """
    api_key = os.getenv("TWINLAB_API_KEY")
    if verbose:
        print("API key: {}".format(api_key))
    return api_key


@typechecked
def user_information(
    verbose: Optional[bool] = False, debug: Optional[bool] = False
) -> dict:
    """
    # User information

    Get information about the user.

    ## Arguments:

    - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
    - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

    ## Returns:

    - `dict` containing user information.

    ## Example:

    ```python
    import twinlab as tl

    user_info = tl.user_information()
    print(user_info)
    ```
    """
    response = api.get_user(verbose=debug)
    user_info = response
    if verbose:
        print("User information:")
        pprint(user_info, compact=True, sort_dicts=False)
    return user_info


@typechecked
def versions(verbose: Optional[bool] = False, debug: Optional[bool] = False) -> dict:
    """
    # twinLab versions

    Get information about the twinLab version being used.

    ## Arguments:

    - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
    - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

    ## Returns:

    - `dict` containing version information.

    ## Example:

    ```python
    import twinlab as tl

    version_info = tl.versions()
    print(version_info)
    ```
    """
    response = api.get_versions(verbose=debug)
    version_info = response
    if verbose:
        print("Version information:")
        pprint(version_info, compact=True, sort_dicts=False)
    return version_info


@typechecked
def list_datasets(
    verbose: Optional[bool] = False, debug: Optional[bool] = False
) -> list:
    """
    # List datasets

    List datasets that have been uploaded to the user's `twinLab` cloud account.

    ## Arguments:

    - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
    - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

    ## Returns:

    - `list` of `str` dataset IDs.

    ## Example:

    ```python
    import pandas as pd
    import twinlab as tl

    datasets = tl.list_datasets()
    print(datasets)
    ```
    """
    response = api.list_datasets(verbose=debug)
    datasets = utils.get_value_from_body("datasets", response)
    if verbose:
        print("Datasets:")
        pprint(datasets, compact=True, sort_dicts=False)
    return datasets


@typechecked
def list_emulators(
    verbose: Optional[bool] = False, debug: Optional[bool] = False
) -> list:
    """
    # List emulators

    List emulators that have been set up in the user's `twinLab` cloud account.

    ## Arguments:

    - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
    - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

    ## Returns:

    - A `list` of `str` campaign IDs.

    ## Example:

    ```python
    import twinlab as tl

    emulators = tl.list_emulators()
    print(emulators)
    ```
    """
    response = api.list_models(verbose=debug)
    campaigns = utils.get_value_from_body("models", response)
    if verbose:
        print("Trained models:")
        pprint(campaigns, compact=True, sort_dicts=False)
    return campaigns
