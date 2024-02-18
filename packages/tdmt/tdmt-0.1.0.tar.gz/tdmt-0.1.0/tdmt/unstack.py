import pandas as pd
from pandas import DataFrame
import utils
from decorators import (
    check_single_input_table,
    validate_ref,
    validate_workflow_tab_present,
    validate_required_columns_on_workflow_tab,
)


@check_single_input_table
@validate_ref
@validate_workflow_tab_present
@validate_required_columns_on_workflow_tab(
    [
        "columns_to_unstack",
        "new_key_name",
        "unstacked_columns_feature_name",
        "unstacked_columns_value_name",
    ]
)
def unstack(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Transforms specified columns of a DataFrame into rows, creating a new key for unique identification and ignoring blanks.

    This operation targets scenarios where data representation benefits from pivoting columns to rows for enhanced analysis.
    It adheres to specifications defined in a workflow map spreadsheet, utilizing designated columns for transformation while
    maintaining data integrity and uniqueness through a newly generated identifier.

    Parameters:
    - input_data_tables: A dictionary containing the DataFrame to be transformed.
    - workflow_map: A dictionary representing the workflow map spreadsheet.
    - ref: The reference within the workflow map detailing the transformation specifics.
    - log: A DataFrame for recording operation messages and errors.

    Returns:
    A dictionary containing the transformed 'dataframe', an empty 'ErrorFrame' for potential errors, and an 'OK_to_continue' flag.
    """
    # Extract specifications from the workflow map
    ref_table = workflow_map[ref]
    columns_to_unstack = ref_table["columns_to_unstack"].dropna().tolist()
    new_key_name = ref_table["new_key_name"].dropna().tolist()[0]
    unstacked_columns_feature_name = (
        ref_table["unstacked_columns_feature_name"].dropna().tolist()[0]
    )
    unstacked_columns_value_name = (
        ref_table["unstacked_columns_value_name"].dropna().tolist()[0]
    )

    # Validate the uniqueness of certain specifications
    for variable in [
        "new_key_name",
        "unstacked_columns_feature_name",
        "unstacked_columns_value_name",
    ]:
        if len(ref_table[variable].dropna().tolist()) > 1:
            utils.print_and_log_message(
                {
                    "message": f"Operation unstack accepts no more than one entry for variable {variable}: {', '.join(ref_table[variable].dropna().tolist())}"
                },
                log,
            )
            return {
                "dataframe": pd.DataFrame(),
                "ErrorFrame": pd.DataFrame(),
                "OK_to_continue": False,
            }

    # Prepare the DataFrame for unstacking
    short_name = next(iter(input_data_tables.keys()))
    input_dataframe = input_data_tables[short_name].reset_index(drop=True)
    other_columns = list(set(input_dataframe.columns) - set(columns_to_unstack))
    input_dataframe["ref"] = input_dataframe.index

    # Perform the unstack operation
    unstacked = (
        input_dataframe.set_index("ref")[columns_to_unstack]
        .unstack()
        .reset_index()
        .rename(
            columns={
                "level_0": unstacked_columns_feature_name,
                0: unstacked_columns_value_name,
            }
        )
    )
    unstacked = unstacked[pd.notnull(unstacked[unstacked_columns_value_name])]

    # Merge the unstacked data with the rest of the columns, sort, and reset the index
    dataframe = (
        pd.merge(
            unstacked, input_dataframe[["ref"] + other_columns], on="ref", how="left"
        )
        .sort_values(
            by=["ref", unstacked_columns_feature_name, unstacked_columns_value_name]
        )
        .drop(columns="ref")
        .reset_index(drop=True)
    )

    # Add a unique identifier to the transformed DataFrame
    utils.add_uuid(dataframe, new_key_name)

    return {
        "dataframe": dataframe,
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": True,
    }
