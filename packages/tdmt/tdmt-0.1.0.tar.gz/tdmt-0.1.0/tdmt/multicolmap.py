import pandas as pd
from pandas import DataFrame
import utils
from decorators import (
    check_single_input_table,
    validate_ref,
    validate_workflow_tab_present,
)


@check_single_input_table
@validate_ref
@validate_workflow_tab_present
def multicolmap(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Maps values from multiple columns in the input DataFrame to a new column based on mappings defined in a workflow map spreadsheet.
    The function requires a reference table with mappings and the name for the new column, which should be the last column
    in the reference table. If the new column name already exists in the input DataFrame, it will be overwritten.

    Parameters:
    - input_data_tables: A dictionary of DataFrames, indexed by their short names.
    - workflow_map: A dictionary containing the workflow map.
    - ref: A string reference to the specific mapping table within the workflow map.
    - log: A DataFrame for logging purposes.

    Returns:
    A dictionary with keys 'dataframe', 'ErrorFrame', and 'OK_to_continue'. The 'dataframe' contains the input DataFrame
    with the new, mapped column added. 'ErrorFrame' captures any rows where mapping could not be applied, and 'OK_to_continue'
    indicates whether the operation was successful.
    """

    # Initialize return object for error cases
    ReturnOnError = {
        "dataframe": pd.DataFrame(),
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": False,
    }

    # Extract DataFrame using the short name
    short_name = next(iter(input_data_tables.keys()))
    dataframe = input_data_tables[short_name].reset_index(drop=True)

    # Extract mapping table from the workflow map
    multicolmap_table = workflow_map[ref]
    multicolmap_columns = list(multicolmap_table.columns)

    # Validate the reference table has at least two columns
    if len(multicolmap_columns) < 2:
        utils.print_and_log_message(
            {
                "message": "Operation multicolmap requires at least two columns on the reference tab."
            },
            log,
        )
        return ReturnOnError

    # Split the columns list into existing and new column names
    multicolmap_existing_columns, multicolmap_new_column = (
        multicolmap_columns[:-1],
        multicolmap_columns[-1],
    )

    # Check if all existing columns are present in the DataFrame
    if not set(multicolmap_existing_columns).issubset(dataframe.columns):
        missing_columns = list(
            set(multicolmap_existing_columns) - set(dataframe.columns)
        )
        utils.print_and_log_message(
            {
                "message": f"Operation multicolmap refers to one or more columns to map that are missing from the input dataframe: {', '.join(missing_columns)}"
            },
            log,
        )
        return ReturnOnError

    # Warn if the new column name already exists in the DataFrame
    if multicolmap_new_column in dataframe.columns:
        utils.print_and_log_message(
            {
                "message": f"Caution: Operation multicolmap is about to overwrite an existing column: {multicolmap_new_column}"
            },
            log,
        )

    # Check for duplicate entries in the mapping table
    if multicolmap_table[multicolmap_existing_columns].duplicated().any():
        utils.print_and_log_message(
            {
                "message": "The reference tab for operation multicolmap has duplicate entries for the mapping columns."
            },
            log,
        )
        return ReturnOnError

    # Handle rows with nulls separately to maintain them in the output
    null_in_map_columns = pd.isnull(dataframe[multicolmap_existing_columns]).any(axis=1)
    hasnull, nonull = (
        dataframe[null_in_map_columns].copy(),
        dataframe[~null_in_map_columns].copy(),
    )

    # Merge non-null rows with the mapping table and recombine with null rows
    nonull = pd.merge(
        nonull, multicolmap_table, on=multicolmap_existing_columns, how="left"
    )
    dataframe = pd.concat([hasnull, nonull]).reset_index(drop=True)

    # Capture rows where mapping could not be applied in the ErrorFrame
    ErrorFrame = dataframe[pd.isnull(dataframe[multicolmap_new_column])]

    return {
        "dataframe": dataframe,
        "ErrorFrame": ErrorFrame,
        "OK_to_continue": True,
    }
