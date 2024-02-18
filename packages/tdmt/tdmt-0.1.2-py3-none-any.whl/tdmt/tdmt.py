import pandas as pd
import argparse
import sys
import os
import importlib
import types
from . import utils
from pandas import DataFrame
from typing import Callable
from skeleton import skeleton

# Configuration variables
input_directory = "input/"
output_directory = "output/"
log_filename_suffix = "_logs"
error_filename_suffix = "_errors"
rounding_decimals = 6

excel_extension='.xlsx'

def main():
    """
    Entry point.
    Parses command-line options to run specified workflow operations on input data.
    Options include specifying the workflow map, running in 'about' or 'versions' mode.
    """
    parser = argparse.ArgumentParser(description='Process an Excel file.')
    # Make excel_file a positional argument but do not enforce as required
    parser.add_argument('excel_file', type=str, nargs='?', help='Excel file to process')

    args = parser.parse_args()

    # Check if the excel_file argument was provided
    if args.excel_file is None:
        print("An Excel file is needed to run this script.")
        parser.print_help()
        # Exit the script gracefully
        sys.exit(1)

    # Ensure the script runs within its directory
    absolute_path = os.path.abspath(__file__)
    directory_name = os.path.dirname(absolute_path)
    os.chdir(directory_name)
    
    # If an Excel file is provided, process it
    try:
        filename=args.excel_file
        has_extension=filename[-len(excel_extension):]==excel_extension
        if has_extension:
            workflow_map_name=filename
        else:
            workflow_map_name=filename+excel_extension
        workflow(workflow_map_name)
        
    except Exception as e:
        print(f"Failed to process the Excel file: {e}")
        sys.exit(1)


def workflow(workflow_map_name: str):
    """
    Executes the data processing workflow specified by the workflow map.

    Parameters:
    - workflow_map_name: The name of the workflow map spreadsheet file detailing operations.
    """
    # Setup output directory
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    log = utils.create_log()
    workflow_map_dict = utils.load_workflow_map(workflow_map_name)
    if not workflow_map_dict["loaded_ok"]:
        return
    workflow_map = workflow_map_dict["workflow_map"]

    # Check for required tabs in the workflow map
    if not {"setup", "raw"}.issubset(workflow_map.keys()):
        print("Workflow file requires at least a setup tab and a raw tab")
        return

    setup_table = workflow_map["setup"]
    runmode = setup_table.loc[0, "runmode"]
    workflow_dict = utils.read_raw_files(input_directory, workflow_map, log)
    if not workflow_dict["loaded_ok"]:
        return

    # Validate run mode and execute accordingly
    if len(setup_table) != 1 or runmode not in ["normal", "skeleton"]:
        print("Runmode on the setup tab must be either normal or skeleton")
        return
    if runmode == "skeleton":
        print("Entering skeleton mode")
        skeleton(workflow_map, workflow_map_name, workflow_dict, output_directory)
    elif runmode == "normal":
        execute_normal_workflow(workflow_map, workflow_dict, log, workflow_map_name)


def execute_normal_workflow(
    workflow_map: dict, workflow_dict: dict, log: DataFrame, workflow_map_name: str
):
    """
    Executes the 'normal' runmode of the workflow, processing input data according to the run list,
    saving processed files, error files, and logs.

    Parameters:
    - workflow_map: The workflow map loaded from the spreadsheet.
    - workflow_dict: A dictionary containing the DataFrames loaded from input files.
    - log: A DataFrame used for logging operation messages.
    - workflow_map_name: The name of the workflow map file.
    """
    run_outputs = runlist(workflow_map, workflow_dict, log)
    OK_to_continue = run_outputs["OK_to_continue"]
    if OK_to_continue:
        OK_to_continue = save_processed_files(workflow_map, workflow_dict, log)
    if OK_to_continue:
        OK_to_continue = save_error_files(run_outputs["error_dict"], log)
    if OK_to_continue:
        logs_dict = {"run_summary": run_outputs["run_summary"], "log": log}
        save_logs(logs_dict, workflow_map_name)


def runlist(workflow_map: dict, workflow_dict: dict, log: DataFrame) -> dict:
    """
    Processes operations defined in the workflow map's runlist tab, applying each operation to the input data tables.

    Parameters:
    - workflow_map: A dictionary representing the workflow map spreadsheet.
    - workflow_dict: A dictionary of DataFrames loaded from input files, keyed by their short names.
    - log: A DataFrame used for logging operation messages and errors.

    Returns:
    A dictionary with keys 'error_dict', 'run_summary', and 'OK_to_continue'. This includes details of any errors encountered,
    a summary of the operations run, and a flag indicating whether all operations completed successfully.
    """
    operations, error_dict = {}, {}
    ReturnOnError = {
        "error_dict": error_dict,
        "run_summary": pd.DataFrame(),
        "OK_to_continue": False,
    }

    # Check for the presence of the runlist tab in the workflow map
    if "runlist" not in workflow_map:
        utils.print_and_log_message(
            {"message": "Workflow file in normal runmode must have a runlist tab"}, log
        )
        return ReturnOnError

    runs = workflow_map["runlist"]
    # Ensure the runlist tab contains all required columns
    if not {"run_id", "short_names_in", "short_name_out", "operation", "ref"}.issubset(
        runs.columns
    ):
        utils.print_and_log_message(
            {
                "message": "Runlist tab requires columns run_id short_names_in short_name_out operation and ref"
            },
            log,
        )
        return ReturnOnError

    run_results = pd.DataFrame(columns=["rows_out", "columns_out", "error_rows"])
    OK_to_continue = True

    # Process each run defined in the runlist
    for run in runs.index:
        ReturnOnErrorDuringRuns = {
            "error_dict": error_dict,
            "run_summary": runs,
            "OK_to_continue": False,
        }
        current_run = runs.loc[run]
        run_id = current_run["run_id"]

        # Validate inputs and operation module
        if pd.isnull(current_run["short_names_in"]):
            utils.print_and_log_message(
                {
                    "message": f"On the runlist tab short_names_in is blank for run_id: {run_id}"
                },
                log,
            )
            return ReturnOnErrorDuringRuns

        short_names_in, short_name_out, operation_name, ref = (
            current_run["short_names_in"].replace(" ", "").split(","),
            current_run["short_name_out"],
            current_run["operation"],
            current_run["ref"],
        )

        if operation_name not in operations:
            try:
                operations[operation_name] = importlib.import_module(operation_name)
            except ImportError:
                utils.print_and_log_message(
                    {
                        "message": f"Error importing module for operation {operation_name}"
                    },
                    log,
                )
                return ReturnOnErrorDuringRuns

        utils.print_and_log_message(
            {
                "message": f"Running {run_id}: {current_run['short_names_in']}: {operation_name}"
            },
            log,
        )

        # Check for missing input data tables
        if not set(short_names_in).issubset(workflow_dict):
            missing_tables = list(set(short_names_in) - set(workflow_dict))
            utils.print_and_log_message(
                {
                    "message": f"Operation {operation_name} requires one or more tables that are missing: {', '.join(missing_tables)}"
                },
                log,
            )
            return ReturnOnErrorDuringRuns

        # Execute the operation
        input_data_tables = {k: workflow_dict[k] for k in short_names_in}
        result_dict = run_operation(
            input_data_tables,
            operations[operation_name],
            operation_name,
            workflow_map,
            ref,
            log,
        )
        result_dict["dataframe"] = (
            result_dict["dataframe"][result_dict["dataframe"].columns.sort_values()]
            .reset_index(drop=True)
            .round(decimals=rounding_decimals)
        )

        workflow_dict[short_name_out], error_dict[run_id] = (
            result_dict["dataframe"],
            result_dict["ErrorFrame"],
        )
        run_results.loc[len(run_results)] = [
            len(workflow_dict[short_name_out]),
            len(workflow_dict[short_name_out].columns),
            len(result_dict["ErrorFrame"]),
        ]

        OK_to_continue = result_dict["OK_to_continue"]
        if not OK_to_continue:
            return ReturnOnErrorDuringRuns

    run_summary = pd.concat([runs, run_results], axis=1)
    return {
        "error_dict": error_dict,
        "run_summary": run_summary,
        "OK_to_continue": True,
    }


def run_operation(
    input_data_tables: dict,
    module: types.ModuleType,
    module_name: str,
    workflow_map: dict,
    ref: str,
    log: DataFrame,
) -> Callable[[dict, dict, str, DataFrame], dict]:
    """
    Executes a specified operation within a module, passing in the necessary data tables, workflow map, reference, and log.

    Parameters:
    - input_data_tables: A dictionary of DataFrames to be processed.
    - module: The Python module containing the operation function.
    - module_name: The name of the function within the module to call.
    - workflow_map: A dictionary representing the workflow map spreadsheet.
    - ref: A reference string used within the operation for specific logic.
    - log: A DataFrame used for logging the process.

    Returns:
    A Callable that when executed will perform the specified operation.
    """
    function = getattr(module, module_name)
    return function(input_data_tables.copy(), workflow_map, ref, log)


def save_processed_files(
    workflow_map: dict, workflow_dict: dict, log: DataFrame
) -> bool:
    """
    Saves the processed data files based on the 'out' tab of the workflow map spreadsheet.

    Parameters:
    - workflow_map: The workflow map detailing the output specifications.
    - workflow_dict: A dictionary containing the processed DataFrames.
    - log: A DataFrame for logging messages.

    Returns:
    A boolean indicating success (True) or failure (False) in saving all files.
    """
    OK_to_continue = True
    if "out" not in workflow_map:
        print("Workflow file has no tab named out. No output files saved.")
        return False

    if not {"short_name", "output_name"}.issubset(workflow_map["out"].columns):
        print(
            "Workflow file tab out requires columns short_name and output_name. No output files saved."
        )
        return False

    out_dict = dict(
        zip(workflow_map["out"].short_name, workflow_map["out"].output_name)
    )
    for k, output_name in out_dict.items():
        utils.print_and_log_message({"message": f"Saving {k}"}, log)

        if k not in workflow_dict:
            utils.print_and_log_message(
                {
                    "message": f"Workflow file tab out refers to a short_name to save that does not exist: {k}"
                },
                log,
            )
            return False

        workflow_dict[k].to_csv(
            os.path.join(output_directory, f"{output_name}.csv"), index=False
        )
    return OK_to_continue


def save_error_files(error_dict: dict, log: DataFrame) -> bool:
    """
    Saves files containing error rows for each operation that encountered errors during processing.

    Parameters:
    - error_dict: A dictionary where each key is a run ID and each value is a DataFrame of error rows for that run.
    - log: A DataFrame for logging messages.

    Returns:
    A boolean indicating success (True) or failure (False) in saving all error files.
    """
    OK_to_continue = True
    for run_id, errors in error_dict.items():
        if not errors.empty:
            utils.print_and_log_message(
                {"message": f"Saving errors for run_id_{run_id}"}, log
            )
            try:
                errors.to_csv(
                    os.path.join(
                        output_directory, f"run_id_{run_id}{error_filename_suffix}.csv"
                    ),
                    index=False,
                )
            except Exception as e:
                utils.print_and_log_message(
                    {
                        "message": f"Error saving error file for run_id_{run_id}{error_filename_suffix}: {e}"
                    },
                    log,
                )
                OK_to_continue = False
    return OK_to_continue


def save_logs(logs_dict: dict, workflow_map_name: str):
    """
    Saves a log file summarizing the operations performed and any messages or errors logged.

    Parameters:
    - logs_dict: A dictionary containing log DataFrames.
    - workflow_map_name: The base name of the workflow map used to generate the log file name.

    Returns:
    None. The function directly saves the log file to the output directory.
    """
    utils.print_and_log_message({"message": "Saving log"}, logs_dict["log"])

    try:
        utils.dict_to_excel(
            logs_dict, output_directory, workflow_map_name[:-5] + log_filename_suffix
        )
    except Exception as e:
        utils.print_and_log_message(
            {
                "message": f"Error saving log {workflow_map_name[:-5]}{log_filename_suffix}: {e}"
            },
            logs_dict["log"],
        )


if __name__ == "__main__":
    main()
