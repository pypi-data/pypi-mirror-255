import pandas as pd
from pandas import DataFrame
import utils


def concat(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Concatenates multiple DataFrames into a single DataFrame.

    Parameters:
    - input_data_tables: A dictionary of DataFrames to be concatenated.
    - workflow_map: A dictionary representing the workflow map (unused).
    - ref: A string reference (unused in the operation but logged).
    - log: A DataFrame for logging purposes.

    Returns:
    A dictionary containing the concatenated DataFrame, an empty DataFrame for errors, and a flag indicating continuation is OK.
    """
    # Log message if ref is used, noting that it is redundant in this context

    if ref == ref:
        utils.print_and_log_message(
            {
                "message": "Operation concat takes no input reference. This value is not being used: "
                + ref
            },
            log,
        )

    # Prepare the list of DataFrames to concatenate
    concat_list = [input_data_tables[key] for key in input_data_tables]

    # Concatenate the DataFrames into a single DataFrame
    dataframe = pd.concat(concat_list, ignore_index=True)

    return {
        "dataframe": dataframe,
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": True,
    }
