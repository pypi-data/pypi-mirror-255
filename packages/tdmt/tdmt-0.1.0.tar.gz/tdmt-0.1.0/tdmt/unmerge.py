from pandas import DataFrame
from decorators import (
    check_single_input_table,
    validate_ref,
    validate_workflow_tab_present,
    validate_required_columns_on_workflow_tab,
)


@check_single_input_table
@validate_ref
@validate_workflow_tab_present
@validate_required_columns_on_workflow_tab(["keys", "other_columns"])
def unmerge(
    input_data_tables: dict, workflow_map: dict, ref: str, log: DataFrame
) -> dict:
    """
    Separates a specified subset from a larger DataFrame based on defined keys and other columns, identifying conflicts.

    This function aims to extract a sub-DataFrame using specified key and non-key columns from the workflow map.
    It also identifies conflicting records with identical key combinations, suggesting potential data integrity issues.

    Parameters:
    - input_data_tables: A dictionary containing the DataFrames, keyed by their names.
    - workflow_map: A dictionary representing the workflow map spreadsheet.
    - ref: A string reference to the specific section within the workflow map detailing the operation.
    - log: A DataFrame used to log operation messages and errors.

    Returns:
    A dictionary with the keys 'dataframe', 'ErrorFrame', and 'OK_to_continue'. 'dataframe' contains the extracted
    sub-DataFrame, 'ErrorFrame' lists any conflicting records, and 'OK_to_continue' indicates success of the operation.
    """
    # Extract the relevant DataFrame and specified columns from the workflow map
    keys, other_columns = (
        workflow_map[ref]["keys"].dropna().tolist(),
        workflow_map[ref]["other_columns"].dropna().tolist(),
    )
    short_name = next(iter(input_data_tables.keys()))
    dataframe = input_data_tables[short_name].reset_index(drop=True)

    # Create a subset DataFrame based on keys and other columns, identifying duplicates
    subset_dataframe = dataframe[keys + other_columns].drop_duplicates().set_index(keys)
    key_counts = subset_dataframe.index.value_counts()
    multiplicity = key_counts[key_counts > 1].index

    # Isolate and log conflicting records
    ErrorFrame = (
        subset_dataframe[subset_dataframe.index.isin(multiplicity)]
        .reset_index()
        .sort_values(by=keys)
    )
    dataframe = subset_dataframe.reset_index().sort_values(by=keys)

    return {"dataframe": dataframe, "ErrorFrame": ErrorFrame, "OK_to_continue": True}
