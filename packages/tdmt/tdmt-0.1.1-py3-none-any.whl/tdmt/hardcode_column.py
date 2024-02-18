import pandas as pd
import numpy as np
from pandas import DataFrame
import utils
from decorators import check_single_input_table, validate_ref


@check_single_input_table
@validate_ref
def hardcode_column(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Adds or replaces a column in the DataFrame with a hardcoded value. The column name and value
    are specified in the `ref` string, using an equal sign '=' to separate the column name from the value.
    If the column already exists, it will be overwritten; otherwise, a new column will be added.
    If there is no equal sign in the ref the new column will be blank for all rows.

    Parameters:
    - input_data_tables: A dictionary of DataFrames, with keys being short names.
    - workflow_map: A dictionary containing the workflow configuration (not used in this function).
    - ref: A string specifying the column name and value, separated by an '='. If no '=' is present,
      the function will add a new column with all values set to NaN.
    - log: A DataFrame used for logging purposes.

    Returns:
    A dictionary with 'dataframe' containing the modified DataFrame, 'ErrorFrame' as an empty DataFrame,
    and 'OK_to_continue' indicating whether the operation was successful.
    """

    # Extract the short name and corresponding DataFrame.
    short_name = next(iter(input_data_tables.keys()))
    dataframe = input_data_tables[short_name].reset_index(drop=True)

    # Process the 'ref' argument for column name and value.
    if "=" in ref:
        column_name, *value_parts = ref.split("=")
        value = "=".join(
            value_parts
        )  # Rejoin remaining parts in case of multiple '=' signs.

        # Validate the number of arguments derived from 'ref'.
        if len(value_parts) > 1:
            utils.print_and_log_message(
                {
                    "message": "Operation hardcode_column requires at most two input arguments."
                },
                log,
            )
            return {
                "dataframe": pd.DataFrame(),
                "ErrorFrame": pd.DataFrame(),
                "OK_to_continue": False,
            }

        # Determine the value to hardcode.
        if value == "":
            value = np.nan
        elif value.isnumeric():
            value = pd.to_numeric(value)
        else:
            value = value

        # Log if replacing an existing column.
        if column_name in dataframe.columns:
            utils.print_and_log_message(
                {"message": f"Replacing existing column with hardcode: {column_name}"},
                log,
            )

        # Set the column with the specified or hardcoded value.
        dataframe[column_name] = value
    else:
        # If 'ref' does not contain '=', add a new column with NaN values.
        if ref in dataframe.columns:
            utils.print_and_log_message(
                {"message": f"Replacing existing column with hardcode: {ref}"}, log
            )
        dataframe[ref] = np.nan

    return {
        "dataframe": dataframe,
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": True,
    }
