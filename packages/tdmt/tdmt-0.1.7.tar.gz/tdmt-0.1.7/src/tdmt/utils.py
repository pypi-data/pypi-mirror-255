import uuid
import os
import pandas as pd
from pandas import DataFrame, Series

# Global settings
print_updates = True
excel_max_column_width = 50
modules_without_versions = {
    "ifs_main_unit_test",
    "ifs_operations_unit_test",
    "diagnostics",
}
table_name_column_name_separator = "$"


def add_uuid(dataframe: DataFrame, uuid_column_name: str):
    """
    Adds a unique identifier to each row of the given DataFrame.

    Parameters:
    - dataframe: The DataFrame to which the UUIDs will be added.
    - uuid_column_name: The name of the column that will store the UUIDs.
    """
    dataframe[uuid_column_name] = [uuid.uuid4() for _ in dataframe.index]


def create_log() -> DataFrame:
    """
    Creates an empty log DataFrame with predefined columns.

    Returns:
    An empty DataFrame structured for logging purposes.
    """
    return pd.DataFrame(columns=["datetime", "message"])


def print_and_log_message(message_dict: dict, log: DataFrame):
    """
    Logs a message to the console and the provided log DataFrame.

    Parameters:
    - message_dict: A dictionary containing the message and possibly other metadata.
    - log: The log DataFrame where the message and metadata are recorded.
    """
    message_string = message_dict.get("message", "")
    message_index = len(log)
    log.loc[message_index, "datetime"] = pd.Timestamp.now()
    log.loc[message_index, "message"] = message_string

    for key, value in message_dict.items():
        if key != "message":
            log.loc[message_index, key] = value
            message_string += f" {key} {value}"

    if print_updates:
        print(message_string)


def dict_to_excel(
    dict_of_sheets: dict, output_directory: str, filename_without_extension: str
):
    """
    Saves a dictionary of DataFrames to an Excel file, each DataFrame as a separate sheet.

    Parameters:
    - dict_of_sheets: A dictionary where keys are sheet names and values are DataFrames.
    - output_directory: The directory where the Excel file will be saved.
    - filename_without_extension: The base name of the output Excel file.
    """
    if dict_of_sheets:
        with pd.ExcelWriter(
            os.path.join(output_directory, f"{filename_without_extension}.xlsx")
        ) as writer:
            for sheet_name, df in dict_of_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                for column in df.columns:
                    column_length = min(
                        excel_max_column_width,
                        max(df[column].astype(str).map(len).max(), len(column)),
                    )
                    column_index = df.columns.get_loc(column)
                    writer.sheets[sheet_name].set_column(
                        column_index, column_index, column_length
                    )
    else:
        print(f"Nothing to print for {filename_without_extension}")


def load_workflow_map(workflow_map_name: str) -> dict:
    """
    Loads a workflow map from an Excel file into a dictionary of DataFrames.

    Parameters:
    - workflow_map_name: The file path of the workflow map Excel file.

    Returns:
    A dictionary containing the loaded workflow map and a status flag.
    """
    if not os.path.exists(workflow_map_name):
        print(f"Workflow map not found: {workflow_map_name}")
        return {"workflow_map": {}, "loaded_ok": False}

    try:
        return {
            "workflow_map": pd.read_excel(workflow_map_name, sheet_name=None),
            "loaded_ok": True,
        }
    except:
        print(f"Error reading workflow map: {workflow_map_name}")
        return {"workflow_map": {}, "loaded_ok": False}


def read_raw_files(input_directory: str, workflow_map: dict, log: DataFrame) -> dict:
    """
    Reads raw data files specified in the 'raw' tab of a workflow map spreadsheet, loading them into a dictionary.

    Parameters:
    - input_directory: The directory containing the raw data files.
    - workflow_map: A dictionary representing the loaded workflow map spreadsheet.
    - log: A DataFrame for logging messages and errors encountered during file reading.

    Returns:
    A dictionary containing DataFrames loaded from raw files and a flag indicating the success of the operation.
    """
    workflow_dict = {"loaded_ok": True}

    # Check if the input directory exists
    if not os.path.exists(input_directory):
        print_and_log_message({"message": f"Missing directory {input_directory}"}, log)
        return {"loaded_ok": False}

    # Validate required columns in the 'raw' tab of the workflow map
    raw_files = workflow_map.get("raw", DataFrame())
    required_columns = {"short_name", "raw_name", "encoding", "separator"}
    if not required_columns.issubset(raw_files.columns):
        print_and_log_message(
            {
                "message": "Workflow file tab raw requires columns raw_name short_name encoding and separator"
            },
            log,
        )
        return {"loaded_ok": False}

    # Process each file specified in the 'raw' tab
    for i, current_file in raw_files.iterrows():
        short_name = current_file["short_name"]
        print_and_log_message({"message": f"Reading {short_name}"}, log)

        # Determine if 'parse_dates' columns are specified and valid
        has_parse_dates = "parse_dates" in raw_files.columns and pd.notnull(
            current_file["parse_dates"]
        )
        parse_dates_columns = (
            current_file["parse_dates"].replace(" ", "").split(",")
            if has_parse_dates
            else None
        )

        file_path = os.path.join(input_directory, f"{current_file['raw_name']}.csv")
        try:
            # Load the file with optional date parsing
            df_kwargs = {
                "encoding": current_file["encoding"],
                "sep": current_file["separator"],
                "parse_dates": parse_dates_columns if has_parse_dates else None,
            }
            workflow_dict[short_name] = pd.read_csv(
                file_path, **{k: v for k, v in df_kwargs.items() if v is not None}
            )
        except:
            print_and_log_message(
                {
                    "message": f"Error reading {short_name}: the parse_dates column on the raw tab refers to one or more columns not present in the target file"
                },
                log,
            )
            return {"loaded_ok": False}

    return workflow_dict


def merge_schema(
    table_dict: dict, merge_detail_table: DataFrame, log: DataFrame
) -> DataFrame:
    OK_to_continue = True
    ReturnOnError = {"merged_table": pd.DataFrame(), "OK_to_continue": False}
    if not {
        "merge_order",
        "short_name",
        "parent_key",
        "child_keys",
        "date_columns",
        "other_columns",
    }.issubset(merge_detail_table.columns):
        print_and_log_message(
            {
                "message": "To merge a schema the guidance table requires columns merge_order short_name parent_key child_keys date_columns and other_columns. One or more of these is missing."
            },
            log,
        )
        return ReturnOnError
    merge_detail = (
        merge_detail_table.copy().sort_values(by="merge_order").reset_index(drop=True)
    )
    for i in merge_detail.index:
        current_row = merge_detail.loc[i]
        short_name = current_row["short_name"]
        parent_key = current_row["parent_key"]
        child_keys = current_row["child_keys"]
        child_keys_list = (
            child_keys.replace(" ", "").split(",") if child_keys == child_keys else []
        )
        date_columns = current_row["date_columns"]
        date_columns_list = (
            date_columns.replace(" ", "").split(",")
            if date_columns == date_columns
            else []
        )
        other_columns = current_row["other_columns"]
        other_columns_list = (
            other_columns.replace(" ", "").split(",")
            if other_columns == other_columns
            else []
        )

        if short_name not in table_dict.keys():
            print_and_log_message(
                {
                    "message": "To merge a schema the guidance table refers to a table that is missing: "
                    + short_name
                },
                log,
            )
            return ReturnOnError
        current_table = table_dict[short_name]
        if not set(child_keys_list).issubset(current_table.columns):
            print_and_log_message(
                {
                    "message": "To merge a schema the guidance table refers to one or more columns that are missing from the table "
                    + short_name
                    + ": "
                    + child_keys
                },
                log,
            )
            return ReturnOnError
        if not set(other_columns_list).issubset(current_table.columns):
            print_and_log_message(
                {
                    "message": "To merge a schema the guidance table refers to one or more columns that are missing from the table "
                    + short_name
                    + ": "
                    + other_columns
                },
                log,
            )
            return ReturnOnError

        if "rownumber" in current_table.columns:
            print_and_log_message(
                {
                    "message": "Trying to add a new column rownumber to table "
                    + short_name
                    + " while merging the schema but this column already exists"
                },
                log,
            )
            return ReturnOnError

        current_table["rownumber"] = current_table.index + 1

        other_columns_list.append("rownumber")

        rename_dict = {
            old_name: short_name + table_name_column_name_separator + old_name
            for old_name in date_columns_list + other_columns_list
        }

        if i == 0:
            merged_table = (
                current_table[child_keys_list + date_columns_list + other_columns_list]
                .copy()
                .rename(columns=rename_dict)
            )
        else:
            if not parent_key in current_table.columns:
                print_and_log_message(
                    {
                        "message": "To merge a schema the guidance table refers to a columns that is missing from the table "
                        + short_name
                        + ": "
                        + parent_key
                    },
                    log,
                )
                return ReturnOnError

            merged_table = pd.merge(
                merged_table,
                current_table[
                    [parent_key]
                    + child_keys_list
                    + date_columns_list
                    + other_columns_list
                ]
                .copy()
                .rename(columns=rename_dict),
                on=parent_key,
                how="left",
            )

    return {"merged_table": merged_table, "OK_to_continue": OK_to_continue}


def convert_percentages(column: Series):
    strip_perc = column.str.rstrip("%")
    strip_perc_num = pd.to_numeric(strip_perc, errors="coerce")
    has_valid_percentages = (
        pd.notnull(strip_perc) & pd.notnull(strip_perc_num) & (strip_perc != column)
    )
    column.loc[has_valid_percentages] = (
        column[has_valid_percentages].str.rstrip("%").astype(float) / 100
    )
