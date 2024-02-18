import pandas as pd
from pandas import DataFrame
import utils
from decorators import (
    check_single_input_table,
    validate_ref,
    validate_workflow_tab_present,
    validate_required_columns_on_workflow_tab,
)

# Global settings
keep_original_columns = True
suffix_for_duplicate_columns = "_orig"
handle_map_exceptions = "leave_unchanged"


@check_single_input_table
@validate_ref
@validate_workflow_tab_present
@validate_required_columns_on_workflow_tab(["old_name", "new_name", "mapref"])
def map_and_rename(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Maps and renames columns in a DataFrame based on specifications from a workflow map spreadsheet.
    This function allows for values within specified columns to be replaced according to
    a mapping table and for columns to be renamed. The function supports keeping original
    columns and handling mapping exceptions according to global settings.

    Parameters:
    - input_data_tables: A dictionary containing DataFrames, keyed by short names.
    - workflow_map: A spreadsheet represented as a dictionary containing the workflow configuration.
    - ref: A reference to a specific configuration within the workflow map.
    - log: A DataFrame for logging messages and errors.

    Returns:
    A dictionary with keys 'dataframe', 'ErrorFrame', and 'OK_to_continue'. 'dataframe'
    contains the modified DataFrame, 'ErrorFrame' captures any rows that could not be
    mapped (based on the handling strategy), and 'OK_to_continue' indicates if the operation
    was successful.
    """

    input_keys_list = list(input_data_tables.keys())
    short_name = input_keys_list[0]
    dataframe = input_data_tables[short_name].reset_index(drop=True)
    map_and_rename_table = workflow_map[ref]
    map_workflow = map_and_rename_table[["old_name", "mapref"]]
    map_workflow = map_workflow[pd.notnull(map_workflow.mapref)].reset_index(drop=True)
    rename_table = map_and_rename_table[["old_name", "new_name"]]
    rename_table = rename_table[pd.notnull(rename_table.new_name)].reset_index(
        drop=True
    )

    if keep_original_columns:
        columns_to_map, columns_to_rename = map_workflow.old_name, rename_table.old_name
        columns_to_map_or_rename = list(
            set(columns_to_map).union(set(columns_to_rename))
        )

        columns_to_map_but_not_rename = list(
            set(columns_to_map) - set(columns_to_rename)
        )

        names_with_suffixes = [
            c + suffix_for_duplicate_columns for c in columns_to_map_but_not_rename
        ]

        rename_dict = dict(zip(columns_to_map_but_not_rename, names_with_suffixes))

        original_columns = (
            dataframe[columns_to_map_or_rename].copy().rename(columns=rename_dict)
        )

    ErrorFrame = pd.DataFrame()

    for i in map_workflow.index:
        current_column = map_workflow.loc[i]
        column_name = current_column["old_name"]
        if current_column["mapref"] not in workflow_map.keys():
            utils.print_and_log_message(
                {
                    "message": "Operation map_and_rename refers to a workflow table that is missing: "
                    + current_column["mapref"]
                },
                log,
            )
            return {
                "dataframe": pd.DataFrame(),
                "ErrorFrame": pd.DataFrame(),
                "OK_to_continue": False,
            }
        current_mapping_table = workflow_map[current_column["mapref"]]
        cat_dict = dict(
            zip(current_mapping_table.old_value, current_mapping_table.new_value)
        )

        if handle_map_exceptions == "leave_unchanged":
            cat_recognised_filter = dataframe[column_name].isin(cat_dict.keys())
            recognised, unrecognised = (
                dataframe[cat_recognised_filter].copy(),
                dataframe[~cat_recognised_filter],
            )
            recognised[column_name] = recognised[column_name].map(cat_dict)
            dataframe = pd.concat([recognised, unrecognised])
            ErrorFrame = pd.concat([ErrorFrame, unrecognised], ignore_index=True)
        elif handle_map_exceptions == "blanks":
            dataframe[column_name] = dataframe[column_name].map(cat_dict)
            ErrorFrame = pd.concat(
                [ErrorFrame, dataframe[pd.isnull(dataframe[column_name])]],
                ignore_index=True,
            )

    rename_dict = dict(zip(rename_table.old_name, rename_table.new_name))

    dataframe = dataframe.rename(columns=rename_dict)
    if keep_original_columns:
        dataframe = pd.concat([dataframe, original_columns], axis=1)

    return {
        "dataframe": dataframe,
        "ErrorFrame": ErrorFrame,
        "OK_to_continue": True,
    }
