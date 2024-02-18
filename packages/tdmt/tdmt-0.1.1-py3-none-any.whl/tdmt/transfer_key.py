import pandas as pd
from pandas import DataFrame
import utils
from decorators import validate_ref


@validate_ref
def transfer_key(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Transfers a specified key from one DataFrame to another based on common key columns, ensuring data integrity by
    excluding records with blank key values and handling duplicates appropriately.

    Parameters:
    - input_data_tables: A dictionary of DataFrames from which and to which the key is to be transferred.
    - workflow_map: A dictionary representing the workflow map, a spreadsheet detailing data processing steps.
    - ref: A string specifying the key to transfer and the columns to use for matching records.
    - log: A DataFrame for logging operation messages and errors.

    Returns:
    A dictionary containing 'dataframe' with the result of the key transfer, 'ErrorFrame' capturing any records
    involved in duplicate key issues, and 'OK_to_continue' indicating whether the operation was successful.
    """

    # Initialize return object for error cases
    ReturnOnError = {
        "dataframe": pd.DataFrame(),
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": False,
    }

    # Ensure exactly two input DataFrames are provided
    input_keys_list = list(input_data_tables.keys())
    if len(input_keys_list) != 2:
        utils.print_and_log_message(
            {
                "message": f"Operation transfer_key requires exactly 2 input dataframes: {', '.join(input_keys_list)}"
            },
            log,
        )
        return ReturnOnError

    # Extract the DataFrames for operation
    left_dataframe, right_dataframe = [
        input_data_tables[key].reset_index(drop=True) for key in input_keys_list
    ]

    # Parse the reference to identify the key to transfer and the existing keys in common
    key_to_transfer, existing_keys_in_common = ref.split("using")
    key_to_transfer = key_to_transfer.strip()
    existing_keys_in_common = [
        key.strip() for key in existing_keys_in_common.split(",")
    ]

    # Filter out records with blanks in the keys from the right DataFrame
    has_blanks_in_keys = right_dataframe[existing_keys_in_common].isnull().any(axis=1)
    dataframe_with_blank_keys, dataframe_nonblank_keys = (
        right_dataframe[has_blanks_in_keys],
        right_dataframe[~has_blanks_in_keys],
    )

    # Perform the merge operation to transfer the key, excluding records with blank keys
    merged_dataframe = pd.merge(
        dataframe_nonblank_keys,
        left_dataframe[[key_to_transfer] + existing_keys_in_common],
        on=existing_keys_in_common,
        how="left",
    )

    # Combine the merged DataFrames and reset the index
    dataframe = (
        pd.concat([merged_dataframe, dataframe_with_blank_keys], ignore_index=True)
        .sort_values(by=key_to_transfer)
        .reset_index(drop=True)
    )

    # Identify records with multiple matches in the merge process
    multiple_matches = (
        dataframe.groupby([key_to_transfer] + existing_keys_in_common)
        .size()
        .reset_index()
        .groupby(existing_keys_in_common)
        .size()
        .reset_index()
    )
    multiple_matches = multiple_matches[multiple_matches[0] > 1].set_index(
        existing_keys_in_common
    )
    ErrorFrame = dataframe[
        dataframe.set_index(existing_keys_in_common).index.isin(multiple_matches.index)
    ]

    return {"dataframe": dataframe, "ErrorFrame": ErrorFrame, "OK_to_continue": True}
