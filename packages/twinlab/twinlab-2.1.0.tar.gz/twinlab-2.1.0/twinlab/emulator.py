# Standard imports
import io
import json
from pprint import pprint
import time
from typing import Optional, Tuple, Union, List

# Third-party imports
from typeguard import typechecked
import pandas as pd

# Project imports
from . import api
from . import utils
from .dataset import Dataset
from .params import (
    TrainParams,
    ScoreParams,
    BenchmarkParams,
    SampleParams,
    PredictParams,
    RecommendParams,
    CalibrateParams,
)

# Converts between acquisiton function 'nice' names and their library names
ACQ_FUNC_DICT = {
    "EI": "EI",
    "qEI": "qEI",
    "LogEI": "LogEI",
    "qLogEI": "qLogEI",
    "PSD": "PSD",
    "qNIPV": "qNIPV",
    "ExpectedImprovement": "EI",
    "qExpectedImprovement": "qEI",
    "LogExpectedImprovement": "LogEI",
    "qLogExpectedImprovement": "qLogEI",
    "PosteriorStandardDeviation": "PSD",
    "qNegIntegratedPosteriorVariance": "qNIPV",
}

PING_TIME_TRAIN_DEFAULT = 5.0  # Seconds
PING_TIME_USE_DEFAULT = 5.0  # Seconds
PROCESSOR_DEFAULT = "cpu"


class Emulator:
    """
    # Emulator

    A class representing a trainable twinLab emulator.

    ## Attributes:

    - `id`: `str`. This is the name of the emulator in the twinLab Cloud.

    ## Methods:

    - `train()`. Performs the training of an emulator on the `twinLab` Cloud.
    - `view()`. Returns the training parameters of a trained emulator on the `twinLab` Cloud.
    - `summarise()`. Returns a statistical summary of a trained emulator on the `twinlab` Cloud.
    - `predict()`. Returns the emulator prediction on the specified input data.
    - `sample()`. Returns samples generated from the posterior distribution of the estimator.
    - `recommend()`. Returns candidate data points from a trained emulator on the `twinLab` Cloud.
    - `calibrate()`. Returns a model that best suits the specified input data.
    - `benchmark()`. Returns a calibration curve for a trained emulator on the `twinlab` Cloud.
    - `delete()`. Deletes an emulator on the `twinlab` Cloud.

    """

    @typechecked
    def __init__(self, id: str):
        self.id = id

    @typechecked
    def train(
        self,
        dataset: Dataset,
        inputs: List[str],
        outputs: List[str],
        params: Optional[TrainParams] = TrainParams(),
        ping_time: Optional[float] = PING_TIME_TRAIN_DEFAULT,
        processor: Optional[str] = PROCESSOR_DEFAULT,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
    ) -> None:
        """
        # Train

        Train an emulator on the `twinLab` Cloud.

        ## Arguments:

        - `dataset`: `Dataset`. twinLab dataset object which contains the training data for the emulator.
        - `inputs`: `list[str]`. List of input names in the training dataset.
        - `outputs`; `list[str]`. List of output names in the training dataset.
        - `ping_time`: `float`, `Optional`. Time  in seconds between pings to the server to check if the job is complete.
        - `processor`: `str`, `Optional`. Processor to use for sampling. Can be either `"cpu"` or `"gpu"`.
        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator.train(dataset, ['X'], ['y'])
        ```
        """

        # Making a dictionary from TrainParams class
        train_dict = params.unpack_parameters()
        train_dict["inputs"] = inputs
        train_dict["outputs"] = outputs
        train_dict["dataset_id"] = dataset.id
        train_dict = utils.coerce_params_dict(train_dict)
        params_str = json.dumps(train_dict)
        response = api.train_model(
            self.id, params_str, processor=processor, verbose=debug
        )
        if verbose:
            message = utils.get_message(response)
            print(message)

        # Wait for job to complete
        complete = False
        while not complete:
            status = self.status(verbose=False, debug=debug)
            complete = utils.get_value_from_body("job_complete", status)
            time.sleep(ping_time)
        if verbose:
            print("Training complete!")

    @typechecked
    def status(
        self, verbose: Optional[bool] = False, debug: Optional[bool] = False
    ) -> dict:
        response = api.get_status_model(self.id, verbose=debug)
        if verbose:
            message = utils.get_message(response)
            print(message)
        return response

    @typechecked
    def view(
        self, verbose: Optional[bool] = False, debug: Optional[bool] = False
    ) -> dict:
        """
        # View

        View an emulator that exists on the `twinLab` Cloud.

        ## Arguments:

        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user. Default is False.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server. Default is False.

        ## Returns:

        - `dict` containing the emulator training parameters.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])
        emulator_params = emulator.view()
        print(emulator_params)
        ```
        """

        response = api.view_model(self.id, verbose=debug)
        model_parameters = response
        if verbose:
            print("Campaign summary:")
            pprint(model_parameters, compact=True, sort_dicts=False)
        return model_parameters

    @typechecked
    def summarise(
        self, verbose: Optional[bool] = False, debug: Optional[bool] = False
    ) -> dict:
        """
        # Summarise

        Get summary statistics for a pre-trained emulator in the `twinLab` Cloud.

        ## Arguments:

        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user. Default is False.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server. Default is False.


        ## Returns:

        - `dict` containing summary statistics for the pre-trained emulator.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])
        info = emulator.summarise()
        print(info)
        ```
        """
        response = api.summarise_model(self.id, verbose=debug)
        summary = response
        if verbose:
            print("Model summary:")
            pprint(summary, compact=True, sort_dicts=False)
        return summary

    @typechecked
    def _use_method(
        self,
        method: str,
        df: Optional[pd.DataFrame] = None,
        df_std: Optional[pd.DataFrame] = None,
        processor: Optional[str] = PROCESSOR_DEFAULT,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
        **kwargs,  # NOTE: This can be *anything*
    ) -> Union[io.StringIO, list, float]:
        if df is not None:
            data_csv = df.to_csv(index=False)
        else:
            data_csv = None
        if df_std is not None:
            data_std_csv = df_std.to_csv(index=False)
        else:
            data_std_csv = None
        response = api.use_model(
            self.id,
            method,
            data_csv=data_csv,
            data_std_csv=data_std_csv,
            processor=processor,
            verbose=debug,
            **kwargs,
        )

        if method in ["predict", "sample", "get_candidate_points", "solve_inverse"]:
            output_csv = utils.get_value_from_body("dataframe", response)
            return io.StringIO(output_csv)
        else:
            output_list = utils.get_value_from_body("result", response)
            return output_list

    @typechecked
    def score(
        self,
        params: Optional[ScoreParams] = ScoreParams(),
        processor: Optional[str] = PROCESSOR_DEFAULT,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
    ) -> list:
        """
        # Score

        Quantify the performance of your trained emulator with an emulator score.

        ## Arguments:

        - `params`: `ScoreParams`, `Optional`. A `ScoreParams` object that contains all necessary scoring parameters.
        - `processor`: `str`, `Optional`. Processor to use for sampling. Can be either `"cpu"` or `"gpu"`.
        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

        ### Returns:

        - `List` containing the trained model score.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])
        df_test = pd.DataFrame({'X': [1.5, 2.5, 3.5]})
        df_mean, df_std = emulator.predict(df_test)
        scores = emulator.score(df_test)
        print(df_mean)
        print(df_std)
        print(scores)
        ```
        """

        list = self._use_method(
            method="score",
            **params.unpack_parameters(),
            processor=processor,
            verbose=verbose,
            debug=debug,
        )
        if verbose:
            print("Emulator Score:")
            print(list)
        return list

    @typechecked
    def benchmark(
        self,
        params: Optional[BenchmarkParams] = BenchmarkParams(),
        processor: Optional[str] = PROCESSOR_DEFAULT,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
    ) -> list:
        """
        # Benchmark

        Quantify the performance of your trained emulator with a calibration curve.

        ## Arguments:

        - `params`: `BenchmarkParams`, `Optional`. A `BenchmarkParams` object that contains all parameters for benchmarking the emulators.
        - `processor`: `str`, `Optional`. Processor to use for sampling. Can be either `"cpu"` or `"gpu"`.
        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

        ## Returns:

        - `List` containing the data for the calibration curve.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)

        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])

        # Plot the calibration curve
        fraction_observed = emulator.benchmark()
        fraction_expected = np.linspace(0,1,fraction_observed.shape[0])

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_title("Calibration curve")
        ax.set_xlabel("Expected coverage")
        ax.set_ylabel("Observed coverage")

        plt.plot(np.linspace(0, 1, 100), fraction_observed)
        plt.plot(np.linspace(0, 1, 100), np.linspace(0, 1, 100), "--")
        plt.show()
        ```
        """

        list = self._use_method(
            method="get_calibration_curve",
            **params.unpack_parameters(),
            processor=processor,
            verbose=verbose,
            debug=debug,
        )
        if verbose:
            print("Calibration curve information:")
            pprint(list)
        return list

    @typechecked
    def predict(
        self,
        df: pd.DataFrame,
        params: Optional[PredictParams] = PredictParams(),
        sync: Optional[bool] = False,
        ping_time: Optional[float] = PING_TIME_USE_DEFAULT,
        processor: Optional[str] = PROCESSOR_DEFAULT,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        # Predict

        Make predictions from a pre-trained emulator that exists on the `twinLab` Cloud.

        ## Arguments:

        - `df`: `pandas.DataFrame`. A `pandas.DataFrame` containing the values to make predictions on.
        - `params`: `PredictParams`. A `PredictParams` object that contains parameters to make predictions.
        - `sync`: `bool`, Optional, determining whether to use synchronous or asynchronous method
        - `ping_time`: `float`, Optional, time between pings to the server to check if the job is complete [s]
        - `processor`: `str`, `Optional`. Processor to use for sampling. Can be either `"cpu"` or `"gpu"`.
        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

        **NOTE:** Evaluation data must be a .csv file, or a `pandas.DataFrame` that is interpretable as a .csv file.

        ## Returns:

        - `tuple` containing:
            - `df_mean`: `pandas.DataFrame` containing mean predictions.
            - `df_std`: `pandas.DataFrame` containing standard deviation predictions.

        ## Example:

        Using a local file:
        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])

        filepath = "path/to/data.csv" # Local
        df_mean, df_std = emulator.predict(filepath)
        print(df_mean)
        print(df_std)
        ```

        Using a `pandas.DataFrame`:
        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])
        df_test = pd.DataFrame({'X': [1.5, 2.5, 3.5]})
        df_mean, df_std = emulator.predict(df_test)
        print(df_mean)
        print(df_std)
        ```
        """

        if sync:
            csv = self._use_method(
                method="predict",
                df=df,
                **params.unpack_parameters(),
                processor=processor,
                verbose=verbose,
                debug=debug,
            )
        else:
            # Send off the request to predict
            response = api.use_request_model(
                model_id=self.id,
                method="predict",
                data_csv=utils.get_csv_string(df),
                **params.unpack_parameters(),
                processor=processor,
                verbose=debug,
            )
            process_id = utils.get_value_from_body("process_id", response)

            # Wait for job to complete
            status = 202
            while status == 202:
                status, response = api.use_response_model(
                    model_id=self.id,
                    method="predict",
                    process_id=process_id,
                    verbose=debug,
                )
                time.sleep(ping_time)

            csv = utils.get_value_from_body("dataframe", response)
            csv = io.StringIO(csv)

        # Munge the response into the mean and std
        df = pd.read_csv(csv, sep=",")
        n = len(df.columns)
        df_mean, df_std = df.iloc[:, : n // 2], df.iloc[:, n // 2 :]
        df_std.columns = df_std.columns.str.removesuffix(" [std_dev]")
        if verbose:
            print("Mean predictions:")
            print(df_mean)
            print("Standard deviation predictions:")
            print(df_std)

        return df_mean, df_std

    @typechecked
    def sample(
        self,
        df: pd.DataFrame,
        num_samples: int,
        params: Optional[SampleParams] = SampleParams(),
        sync: Optional[bool] = False,
        ping_time: Optional[float] = PING_TIME_USE_DEFAULT,
        processor: Optional[str] = PROCESSOR_DEFAULT,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        # Sample

        Draw samples from a pre-trained emulator that exists on the `twinLab` Cloud.

        ## Arguments:

        - `df` : `pandas.DataFrame`. A `pandas.DataFrame` containing the values to sample from.
        - `num_samples`: `int`. Number of samples to draw for each row of the evaluation data.
        - `params`: `SampleParams`, `Optional`. A `SampleParams` object with sampling parameters.
        - `sync`: `bool`, `Optional`. If true, send synchronous cloud request, else send asynchronous request.
        - `ping_time`: `float`, `Optional`. Time in seconds to wait between each synchronous results response fetch.
        - `processor`: `str`, `Optional`. Processor to use for sampling. Can be either `"cpu"` or `"gpu"`.
        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

        **NOTE:** Evaluation data must be a .csv file, or a `pandas.DataFrame` that is interpretable as a .csv file.

        ## Returns:

        - `pandas.DataFrame` with the sampled values.

        ## Example:

        Using a local file:
        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)

        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])
        filepath = "path/to/data.csv" # Local
        n = 10
        df_mean, df_std = emulator.sample(filepath, n)
        print(df_mean)
        print(df_std)
        ```

        Using a `pandas.DataFrame`:
        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])
        df = pd.DataFrame({'X': [1.5, 2.5, 3.5]})
        n = 10
        df_mean, df_std = emulator.sample(df, n)
        print(df_mean)
        print(df_std)
        ```
        """

        if sync:
            csv = self._use_method(
                method="sample",
                df=df,
                num_samples=num_samples,
                **params.unpack_parameters(),
                processor=processor,
                verbose=verbose,
                debug=debug,
            )
        else:
            # Send off the request to predict
            response = api.use_request_model(
                model_id=self.id,
                method="sample",
                data_csv=utils.get_csv_string(df),
                num_samples=num_samples,
                **params.unpack_parameters(),
                processor=processor,
                verbose=debug,
            )
            process_id = utils.get_value_from_body("process_id", response)

            # Wait for job to complete
            status = 202
            while status == 202:
                status, response = api.use_response_model(
                    model_id=self.id,
                    method="sample",
                    process_id=process_id,
                    verbose=debug,
                )
                time.sleep(ping_time)

            csv = utils.get_value_from_body("dataframe", response)
            csv = io.StringIO(csv)

        # Return results
        df_result = pd.read_csv(csv, header=[0, 1], sep=",")
        if verbose:
            print("Samples:")
            print(df_result)
        return df_result

    @typechecked
    def recommend(
        self,
        num_points: int,
        acq_func: str,
        params: Optional[RecommendParams] = RecommendParams(),
        sync: Optional[bool] = False,
        ping_time: Optional[float] = PING_TIME_USE_DEFAULT,
        processor: Optional[str] = PROCESSOR_DEFAULT,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
         # Recommend

         Draw new candidate data points via active learning from a pre-trained emulator
         that exists on the `twinLab` Cloud.

         ## Arguments:
         - `num_points`: `int`. Number of samples to draw for each row of the evaluation data.
         - `acq_func`: `str`. Specifies the acquisition function to be used when recommending new points; this can be chose from a list of possible fucntions:
         `"ExpectedImprovement"`, `"qExpectedImprovement"`, `"LogExpectedImprovement"`, `"qLogExpectedImprovement"`, `"PosteriorStandardDeviation"`, `"qNegIntegratedPosteriorVariance"`.
         - `params`: `RecommendParams`, `Optional`. A `RecommendParams` object that contains all recommendation parameters.
        - `sync`: `bool`, `Optional`. If true, send synchronous cloud request, else send asynchronous request.
         - `ping_time`: `float`, `Optional`. Time  in seconds between pings to the server to check if the job is complete.
         - `processor`: `str`, `Optional`. Processor to use for sampling. Can be either `"cpu"` or `"gpu"`.
         - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
         - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

         ## Returns:

         - `pandas.DataFrame` containing the recommended sample locations.

         ## Example:

         ```python
         import pandas as pd
         import twinlab as tl

         df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
         dataset = tl.Dataset("my_dataset")
         dataset.upload(df)

         emulator = tl.Emulator("emulator_id")
         emulator.train(dataset, ['X'], ['y'])
         n = 10
         df = emulator.recommend(n, 'qEI')
         print(df)
         ```
        """

        if sync:
            csv = self._use_method(
                model_id=self.id,
                method="get_candidate_points",
                num_points=num_points,
                acq_func=ACQ_FUNC_DICT[acq_func],
                **params.unpack_parameters(),
                processor=processor,
                verbose=verbose,
                debug=debug,
            )

        else:
            # Send off the request to recommend
            response = api.use_request_model(
                model_id=self.id,
                method="get_candidate_points",
                num_points=num_points,
                acq_func=ACQ_FUNC_DICT[acq_func],
                **params.unpack_parameters(),
                processor=processor,
                verbose=debug,
            )
            process_id = utils.get_value_from_body("process_id", response)

            # Wait for job to complete
            status = 202
            while status == 202:
                status, response = api.use_response_model(
                    model_id=self.id,
                    method="get_candidate_points",
                    process_id=process_id,
                    verbose=debug,
                )
                time.sleep(ping_time)

            csv = utils.get_value_from_body("dataframe", response)
            csv = io.StringIO(csv)

        df = pd.read_csv(csv, sep=",")
        if verbose:
            print("Recommended samples:")
            print(df)

        return df

    @typechecked
    def calibrate(
        self,
        df_obs: pd.DataFrame,
        df_std: pd.DataFrame,
        params: Optional[CalibrateParams] = CalibrateParams(),
        sync: Optional[bool] = False,
        ping_time: Optional[float] = PING_TIME_USE_DEFAULT,
        processor: Optional[str] = PROCESSOR_DEFAULT,
        verbose: Optional[bool] = False,
        debug: Optional[bool] = False,
    ) -> pd.DataFrame:
        """
        # Calibrate

        Given a set of observations, inverse modelling finds the model that would best suit the data.

        ## Arguments:

        - `df_obs` : `pandas.DataFrame`. A `pandas.DataFrame` containing the observations.
        - `df_std` : `pandas.DataFrame`. A `pandas.DataFrame` containing the error on the observations.
        - `params`: `CalibrateParams`, `Optional`. A `CalibrateParams` object that contains all calibration parameters.
        - `sync`: `bool`, Optional, determining whether to use synchronous or asynchronous method
        - `ping_time`: `float`, Optional, time between pings to the server to check if the job is complete [s]
        - `processor`: `str`, `Optional`. Processor to use for sampling. Can be either `"cpu"` or `"gpu"`.
        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

        ## Returns:

        - `pandas.DataFrame` containing the recommended model statistics.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])
        data_csv = pd.DataFrame({'y': [1]})
        data_std_csv = pd.DataFrame({'y': [0.498]})
        df = emulator.calibrate(data_csv, data_std_csv)
        print(df)
        ```
        """

        if sync:
            csv = self._use_method(
                method="solve_inverse",
                df=df_obs,
                df_std=df_std,
                **params.unpack_parameters(),
                processor=processor,
                verbose=verbose,
                debug=debug,
            )

            df = pd.read_csv(csv, sep=",")

        else:
            # Send off the request to predict
            response = api.use_request_model(
                model_id=self.id,
                method="solve_inverse",
                data_csv=utils.get_csv_string(df_obs),
                data_std_csv=utils.get_csv_string(df_std),
                **params.unpack_parameters(),
                processor=processor,
                verbose=debug,
            )
            process_id = utils.get_value_from_body("process_id", response)

            # Wait for job to complete
            status = 202
            while status == 202:
                status, response = api.use_response_model(
                    model_id=self.id,
                    method="solve_inverse",
                    process_id=process_id,
                    verbose=debug,
                )
                time.sleep(ping_time)

            # convert to csv
            csv = utils.get_value_from_body("dataframe", response)
            csv = io.StringIO(csv)

            # deal with Unnamed column in summary table
            # TODO: This seems like a nasty hack
            df = pd.read_csv(csv, sep=",")
            df = df.set_index("Unnamed: 0")
            df.index.name = None
            if "Unnamed: 0.1" in df.columns:
                df = df.drop("Unnamed: 0.1", axis=1)

        if verbose:
            print("Inverse model statistics:")
            print(df)

        return df

    @typechecked
    def delete(
        self, verbose: Optional[bool] = False, debug: Optional[bool] = False
    ) -> None:
        """
        # Delete

        Delete emulator from the `twinLab` Cloud.

        ## Arguments:

        - `verbose`: `bool`, `Optional`. Determining level of information returned to the user.
        - `debug`: `bool`, `Optional`. Determining level of information logged on the server.

        ## Example:

        ```python
        import pandas as pd
        import twinlab as tl

        df = pd.DataFrame({'X': [1, 2, 3, 4], 'y': [1, 4, 9, 16]})
        dataset = tl.Dataset("my_dataset")
        dataset.upload(df)
        emulator = tl.Emulator("emulator_id")
        emulator.train(dataset, ['X'], ['y'])

        emulator.delete()
        ```
        """

        response = api.delete_model(self.id, verbose=debug)
        if verbose:
            message = utils.get_message(response)
            print(message)
