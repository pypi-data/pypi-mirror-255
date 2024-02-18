import pandas as pd
from pandas import DataFrame
import utils
from decorators import check_single_input_table, validate_ref


@check_single_input_table
@validate_ref
def add_key(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Adds a unique identifier to the input DataFrame based on a reference string.

    Parameters:
    - input_data_tables: A dictionary of DataFrames.
    - workflow_map: A dictionary mapping workflow steps.
    - ref: A reference string used to generate the unique identifier.
    - log: A DataFrame for logging purposes.

    Returns:
    A dictionary containing the modified DataFrame, an empty error DataFrame, and a flag indicating it is OK to continue.
    """
    # Extract the short name from the input data tables' keys
    input_keys_list = list(input_data_tables.keys())
    short_name = input_keys_list[0]

    # Reset index of the DataFrame to ensure continuity
    dataframe = input_data_tables[short_name].reset_index(drop=True)

    # Add a unique identifier to the DataFrame
    utils.add_uuid(dataframe, ref)

    return {
        "dataframe": dataframe,
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": True,
    }
