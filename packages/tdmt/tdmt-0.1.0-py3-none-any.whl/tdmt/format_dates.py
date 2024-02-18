import pandas as pd
from pandas import DataFrame
from decorators import (
    check_single_input_table,
    validate_ref,
    validate_workflow_tab_present,
    validate_required_columns_on_workflow_tab,
    verify_short_name_present_on_ref_tab,
)


@check_single_input_table
@validate_ref
@validate_workflow_tab_present
@verify_short_name_present_on_ref_tab
@validate_required_columns_on_workflow_tab(
    ["short_name", "date_column_name", "formatstring"]
)
def format_dates(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Formats the date columns of a DataFrame based on the format strings specified in the workflow map spreadsheet.

    The function applies formatting to each date column mentioned in the workflow map for the given reference (ref).
    It validates the input data table to ensure there's only one, checks the reference, confirms the workflow tab's presence,
    ensures the short name is present on the reference tab, and verifies required columns are present.

    Parameters:
    - input_data_tables: A dictionary containing DataFrames, keyed by their short names.
    - workflow_map: A dictionary representing the workflow map, keyed by references.
    - ref: A string specifying the reference tab in the workflow map.
    - log: A DataFrame for logging any messages or errors.

    Returns:
    A dictionary with the keys 'dataframe', 'ErrorFrame', and 'OK_to_continue',
    where 'dataframe' is the modified DataFrame, 'ErrorFrame' collects any rows that
    could not be formatted, and 'OK_to_continue' is a boolean flag indicating the
    operation's success.
    """

    # Initialize an empty DataFrame for collecting errors.
    ErrorFrame = pd.DataFrame()

    # Extract the short name from the input data tables and the corresponding DataFrame.
    short_name = next(iter(input_data_tables.keys()))
    dataframe = input_data_tables[short_name].reset_index(drop=True)

    # Filter the dates information for the current short name.
    dates = workflow_map[ref][workflow_map[ref].short_name == short_name].reset_index(
        drop=True
    )

    for i in dates.index:
        current_column_name, formatstring = dates.loc[
            i, ["date_column_name", "formatstring"]
        ]
        current_column = dataframe[current_column_name].copy().astype(str)
        already_blank = pd.isnull(current_column)

        # Apply date formatting, handling NaN values and incorrect formats.
        formatted_column_name = "formatted_date"
        if pd.isna(formatstring):
            dataframe[formatted_column_name] = pd.to_datetime(
                pd.to_datetime(current_column, errors="coerce").dt.date
            )
        else:
            dataframe[formatted_column_name] = pd.to_datetime(
                pd.to_datetime(
                    current_column, errors="coerce", format=formatstring
                ).dt.date
            )

        # Identify new blank entries post-formatting and concatenate them to the ErrorFrame.
        new_blanks = ~already_blank & pd.isnull(dataframe[formatted_column_name])
        dataframe = dataframe.drop(columns=current_column_name).rename(
            columns={formatted_column_name: current_column_name}
        )
        ErrorFrame = pd.concat([ErrorFrame, dataframe[new_blanks]])

    # Reset index for the final DataFrame to ensure clean output.
    dataframe.reset_index(drop=True, inplace=True)

    # Return the formatted DataFrame, an empty ErrorFrame (for consistency with the input format), and a success flag.
    return {
        "dataframe": dataframe,
        "ErrorFrame": ErrorFrame if not ErrorFrame.empty else pd.DataFrame(),
        "OK_to_continue": True,
    }
