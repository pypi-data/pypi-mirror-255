# Standard imports
import io
from typing import Optional

# Third-party imports
import pandas as pd
from typeguard import typechecked

# Project imports
from . import api
from . import settings
from . import utils


class Dataset:
    """
    # Datasets for twinLab

    A twinLab dataset that can be used for training an emulator online.

    ## Arguments:
    - `id`: `str`. Name of the dataset.
    """

    def __init__(self, id: str):
        self.id = id

    def __str__(self):
        return f"Dataset ID: {self.id}"

    @typechecked
    def upload(
        self,
        df: pd.DataFrame,
        use_upload_url: Optional[bool] = True,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
    ) -> None:
        """
        # Upload

        Upload a dataset to the user's `twinLab` cloud account so that it can be queried and used for training.

        ## Arguments:

        - `df`: `pandas.DataFrame`. A `pandas.DataFrame` containing the desired dataset.
        - `use_upload_url`: `bool`, `Optional`. Determining whether to upload via a pre-signed url or directly to the server.
        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user. Default is False.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server. Default is False.

        ## Examples:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        ```
        """

        # Upload the file (either via link or directly)
        if use_upload_url:
            response = api.generate_upload_url(self.id, verbose=debug)
            upload_url = utils.get_value_from_body("url", response)
            utils.upload_dataframe_to_presigned_url(
                df,
                upload_url,
                verbose=verbose,
                check=settings.CHECK_DATASETS,
            )
            if verbose:
                print("Processing dataset")
            response = api.process_uploaded_dataset(self.id, verbose=debug)

        else:
            csv_string = utils.get_csv_string(df)
            response = api.upload_dataset(self.id, csv_string, verbose=debug)
        if verbose:
            message = utils.get_message(response)
            print(message)

    # TODO: This should possibly be called 'download' instead of 'view'
    @typechecked
    def view(
        self, verbose: Optional[bool] = False, debug: Optional[bool] = False
    ) -> pd.DataFrame:
        """
        # View datasets

        View a dataset that exists on the user's twinLab cloud account.

        ## Arguments:

        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user. Default is False.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server. Default is False.

        ## Returns:

        - `pandas.DataFrame` of the dataset.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        df = dataset.view()
        print(df)
        ```
        """
        response = api.view_dataset(self.id, verbose=debug)
        csv_string = utils.get_value_from_body("dataset", response)
        csv_string = io.StringIO(csv_string)
        df = pd.read_csv(csv_string, sep=",")
        if verbose:
            print("Dataset:")
            print(df)
        return df

    @typechecked
    def summarise(
        self, verbose: Optional[bool] = False, debug: Optional[bool] = False
    ) -> pd.DataFrame:
        """
        # Summarise datasets

        Summarise a dataset that exists on the user's `twinLab` cloud account by printing summary statistics.

        ## Arguments:

        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user. Default is False.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server. Default is False.

        ## Returns:

        - `pandas.DataFrame` containing summary statistics for the dataset.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        df_summary = dataset.summarise()
        print(df_summary)
        ```
        """
        response = api.summarise_dataset(self.id, verbose=debug)
        csv_string = utils.get_value_from_body("dataset_summary", response)
        csv_string = io.StringIO(csv_string)
        df = pd.read_csv(csv_string, index_col=0, sep=",")
        if verbose:
            print("Dataset summary:")
            print(df)
        return df

    @typechecked
    def delete(
        self, verbose: Optional[bool] = False, debug: Optional[bool] = False
    ) -> None:
        """
        # Delete datasets

        Delete a dataset from the user's `twinLab` cloud account.

        ## Arguments:

        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user. Default is False.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server. Default is False.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        dataset.delete()
        ```
        """
        response = api.delete_dataset(self.id, verbose=debug)
        if verbose:
            message = utils.get_message(response)
            print(message)
