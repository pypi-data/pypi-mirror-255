from typing import Callable, Dict
import pandas as pd
from pandas import DataFrame
import utils
from functools import wraps

# A default return object for when an error occurs in any of the operations.
ReturnOnError = {
    "dataframe": pd.DataFrame(),
    "ErrorFrame": pd.DataFrame(),
    "OK_to_continue": False,
}


def verify_short_name_present_on_ref_tab(func: Callable) -> Callable:
    """
    Decorator to verify if the selected table short name is referred to on the reference tab of the workflow map spreadsheet.
    If not present, logs an error message and returns a default error object.
    """

    @wraps(func)
    def wrapper(
        input_data_tables: Dict[str, DataFrame],
        workflow_map: Dict[str, pd.DataFrame],
        ref: str,
        log: DataFrame,
        *args,
        **kwargs,
    ) -> Dict:
        short_name = next(iter(input_data_tables.keys()))
        reftab = workflow_map.get(ref, pd.DataFrame())
        if short_name not in reftab["short_name"].values:
            message = (
                f"The operation is instructed to use the table {short_name} in association "
                f"with workflow tab {ref} but {short_name} is missing from the {ref} tab. "
                "Please check both tabs."
            )
            utils.print_and_log_message({"message": message}, log)
            return ReturnOnError
        return func(input_data_tables, workflow_map, ref, log, *args, **kwargs)

    return wrapper


def validate_workflow_tab_present(func: Callable) -> Callable:
    """
    Decorator to check if the referenced workflow tab (ref) exists within the workflow map spreadsheet.
    If the tab is missing, logs an error message and returns a default error object.
    """

    @wraps(func)
    def wrapper(
        input_data_tables: Dict[str, DataFrame],
        workflow_map: Dict[str, pd.DataFrame],
        ref: str,
        log: DataFrame,
        *args,
        **kwargs,
    ) -> Dict:
        if ref not in workflow_map:
            message = f"Operation refers to a workflow tab that is missing: {ref}"
            utils.print_and_log_message({"message": message}, log)
            return ReturnOnError
        return func(input_data_tables, workflow_map, ref, log, *args, **kwargs)

    return wrapper


def validate_required_columns_on_workflow_tab(required_columns: [str]) -> Callable:
    """
    Decorator factory that takes a list of required columns and returns a decorator.
    The decorator checks if these columns are present on the reference tab of the workflow map spreadsheet.
    If any required columns are missing, logs an error message and returns a default error object.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(
            input_data_tables: Dict[str, DataFrame],
            workflow_map: Dict[str, pd.DataFrame],
            ref: str,
            log: DataFrame,
            *args,
            **kwargs,
        ) -> Dict:
            filters = workflow_map.get(ref, pd.DataFrame())
            if not set(required_columns).issubset(filters.columns):
                missing_columns = set(required_columns) - set(filters.columns)
                message = "Operation requires columns {}, and one or more are missing: {}".format(
                    ", ".join(required_columns), ", ".join(missing_columns)
                )
                utils.print_and_log_message({"message": message}, log)
                return ReturnOnError
            return func(input_data_tables, workflow_map, ref, log, *args, **kwargs)

        return wrapper

    return decorator


def check_single_input_table(func: Callable) -> Callable:
    """
    Decorator to ensure only a single input table is provided to the operation.
    If multiple tables are found, logs an error message and returns a default error object.
    """

    @wraps(func)
    def wrapper(
        input_data_tables: Dict[str, DataFrame],
        workflow_map: Dict[str, pd.DataFrame],
        ref: str,
        log: DataFrame,
    ) -> Dict:
        if len(input_data_tables) > 1:
            utils.print_and_log_message(
                {
                    "message": "Operation does not support multiple input dataframes: "
                    + ", ".join(input_data_tables.keys())
                },
                log,
            )
            return ReturnOnError
        return func(input_data_tables, workflow_map, ref, log)

    return wrapper


def validate_ref(func: Callable) -> Callable:
    """
    Decorator to validate that the relevant reference cell in the workflow map spreadsheet is not blank.
    If it is, logs an error and returns a default error object.
    """

    @wraps(func)
    def wrapper(
        input_data_tables: Dict[str, DataFrame],
        workflow_map: Dict[str, pd.DataFrame],
        ref: str,
        log: DataFrame,
        *args,
        **kwargs,
    ) -> Dict:
        if ref != ref:  # This is always True; serves as a placeholder.
            message = (
                "Operation requires a non-empty string reference in the ref column"
            )
            utils.print_and_log_message({"message": message}, log)
            return ReturnOnError
        else:
            return func(input_data_tables, workflow_map, ref, log, *args, **kwargs)

    return wrapper
