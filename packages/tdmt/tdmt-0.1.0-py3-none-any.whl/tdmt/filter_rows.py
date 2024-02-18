import pandas as pd
from pandas import DataFrame
import utils
from decorators import (
    check_single_input_table,
    validate_ref,
    validate_workflow_tab_present,
    validate_required_columns_on_workflow_tab,
)

# Define supported filter types
supported_filters = {"must_start_with_one_of", "must_not_start_with"}


@check_single_input_table
@validate_ref
@validate_workflow_tab_present
@validate_required_columns_on_workflow_tab(
    ["old_name", "leading_characters", "filter_type"]
)
def filter_rows(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Filters rows in a DataFrame based on filter criteria specified in the workflow map spreadsheet.

    Decorators are used to validate the input data tables, reference, and workflow tab presence,
    as well as ensuring required columns are present in the workflow tab.

    Parameters:
    - input_data_tables: A dictionary of DataFrames.
    - workflow_map: A dictionary containing the workflow map.
    - ref: A string reference to a specific workflow tab.
    - log: A DataFrame used for logging.

    Returns:
    A dictionary containing the filtered DataFrame, an empty error DataFrame, and a flag indicating continuation.
    """

    # Get the short name from the input data tables
    short_name = next(iter(input_data_tables.keys()))
    dataframe = input_data_tables[short_name].reset_index(drop=True)

    # Retrieve filters from the workflow map using the reference
    filters = workflow_map[ref]
    filter_types = set(pd.unique(filters["filter_type"]))

    # Check if all filter types are supported
    if not filter_types.issubset(supported_filters):
        unexpected_types_list = list(filter_types - supported_filters)
        utils.print_and_log_message(
            {
                "message": (
                    "Operation filter_rows supports only filter_type must_start_with_one_of and "
                    "must_not_start_with but unexpected values were provided: "
                    + ", ".join(unexpected_types_list)
                )
            },
            log,
        )
        return {
            "dataframe": pd.DataFrame(),
            "ErrorFrame": pd.DataFrame(),
            "OK_to_continue": False,
        }

    # Apply filters to the dataframe
    for i in filters.index:
        current_row = filters.loc[i]
        char_pattern = current_row["leading_characters"]
        column_name = current_row["old_name"]
        filter_type = current_row["filter_type"]

        # Filter based on the filter type
        if filter_type == "must_start_with_one_of":
            or_list = [x for x in char_pattern.replace(" ", "").split(",") if x]
            current_filter = pd.concat(
                [dataframe[column_name].str.startswith(text) for text in or_list],
                axis=1,
            ).any(axis=1)

        elif filter_type == "must_not_start_with":
            current_filter = (
                ~dataframe[column_name].str.startswith(char_pattern)
                if char_pattern
                else pd.notnull(dataframe[column_name])
            )

        dataframe = dataframe[current_filter]

    dataframe = dataframe.reset_index(drop=True)

    return {
        "dataframe": dataframe,
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": True,
    }
