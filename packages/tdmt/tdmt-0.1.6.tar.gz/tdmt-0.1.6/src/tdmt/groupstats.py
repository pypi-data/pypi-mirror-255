import pandas as pd
from pandas import DataFrame
import utils
from decorators import (
    check_single_input_table,
    validate_ref,
    validate_workflow_tab_present,
    verify_short_name_present_on_ref_tab,
    validate_required_columns_on_workflow_tab,
)


@check_single_input_table
@validate_ref
@validate_workflow_tab_present
@verify_short_name_present_on_ref_tab
@validate_required_columns_on_workflow_tab(
    ["short_name", "group_keys", "group_target", "operator", "grouped_column_name"]
)
def groupstats(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Applies group-based statistical operations to a DataFrame and generates a new column with the results.

    This function groups rows based on specified keys and calculates a summary statistic (e.g., sum, min, max)
    for each group. The result is added to the DataFrame as a new column. The function is configured through
    a workflow map spreadsheet which specifies the grouping keys, target column for calculation, the operation to perform,
    and the name for the new column.

    Parameters:
    - input_data_tables: A dictionary of DataFrames, indexed by their short names.
    - workflow_map: A dictionary containing the workflow configuration.
    - ref: A string reference to a specific configuration within the workflow map.
    - log: A DataFrame for logging messages and errors.

    Returns:
    A dictionary with 'dataframe', 'ErrorFrame', and 'OK_to_continue' keys. The 'dataframe' contains the original
    DataFrame with the new, calculated column added. 'ErrorFrame' is an empty DataFrame in this setup, and
    'OK_to_continue' indicates whether the operation completed successfully.
    """

    ReturnOnError = {
        "dataframe": pd.DataFrame(),
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": False,
    }

    short_name = next(iter(input_data_tables.keys()))
    dataframe = input_data_tables[short_name].reset_index(drop=True)
    stats = workflow_map[ref]

    # Check for any null values in the configuration
    if pd.isnull(stats).any().any():
        utils.print_and_log_message(
            {
                "message": "Operation groupstats requires columns in the relevant workflow spreadsheet tab to have no blank values. One or more values are blank."
            },
            log,
        )
        return ReturnOnError

    stats = stats[stats.short_name == short_name].reset_index(drop=True)

    for i in stats.index:
        current_stat = stats.loc[i]

        group_key_list = current_stat["group_keys"].replace(" ", "").split(",")
        group_target = current_stat["group_target"]
        operator = current_stat["operator"]
        grouped_column_name = current_stat["grouped_column_name"]

        # Ensure all required columns are present
        columns_used = group_key_list + [group_target]
        if not set(columns_used).issubset(dataframe.columns):
            columns_missing_string = ", ".join(
                set(columns_used) - set(dataframe.columns)
            )
            utils.print_and_log_message(
                {
                    "message": f"Operation groupstats refers to one or more columns that are missing from the data: {columns_missing_string}"
                },
                log,
            )
            return ReturnOnError

        # Perform group operation and merge results
        group_map = (
            dataframe.groupby(group_key_list)[group_target]
            .agg(operator)
            .reset_index()
            .rename(columns={group_target: grouped_column_name})
        )
        dataframe = pd.merge(dataframe, group_map, on=group_key_list, how="left")

    dataframe.reset_index(drop=True, inplace=True)

    return {
        "dataframe": dataframe,
        "ErrorFrame": pd.DataFrame(),
        "OK_to_continue": True,
    }
