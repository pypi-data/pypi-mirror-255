import pandas as pd
import numpy as np
from utils import dict_to_excel

# Global constants
skeleton_filename_suffix = "_skel"
default_skeleton_operation_name = "map_and_rename"
default_skeleton_ref_suffix = "_mr1"
skeleton_update_suffix = "_updated"
skeleton_column_summary_table_suffix = "_summary"
skeleton_top_n_entries = 1000


def skeleton(
    workflow_map: dict,
    workflow_map_name: str,
    workflow_dict: dict,
    output_directory: str,
):
    """
    Automates the preparation of a workflow map spreadsheet based on provided data. This includes generating
    run lists for mapping and renaming operations, creating reference tables for mappings, and summarizing data
    for mapped columns. The results are saved as Excel files in the specified output directory.

    Parameters:
    - workflow_map: A dictionary representing the initial workflow map.
    - workflow_map_name: The name of the workflow map file.
    - workflow_dict: A dictionary containing DataFrames for each short name in the workflow.
    - output_directory: The directory where the output Excel files will be saved.
    """
    column_summaries = {}
    worksheets = workflow_map.keys()
    raw_files = workflow_map["raw"]

    # Prepare the run list for mapping and renaming operations
    if "runlist" not in worksheets:
        runlist = _prepare_runlist(
            raw_files, workflow_dict, workflow_map, column_summaries
        )
        workflow_map["runlist"] = runlist
    else:
        _update_runlist(workflow_map, worksheets, workflow_dict, column_summaries)

    # Prepare the 'out' worksheet if not already present
    _prepare_out_worksheet(workflow_map, worksheets)

    # Save the updated workflow map and column summaries to Excel
    dict_to_excel(
        workflow_map,
        output_directory,
        workflow_map_name[:-5] + skeleton_filename_suffix,
    )
    dict_to_excel(
        column_summaries,
        output_directory,
        workflow_map_name[:-5] + skeleton_column_summary_table_suffix,
    )


def _prepare_runlist(raw_files, workflow_dict, workflow_map, column_summaries):
    """
    Prepares the initial run list for the workflow map based on the raw files provided.

    Parameters:
    - raw_files: DataFrame containing information on raw files to be processed.
    - workflow_dict: Dictionary containing DataFrames for each short name in the workflow.
    - workflow_map: The initial workflow map dictionary to be updated.
    - column_summaries: Dictionary to store column summaries for each short name.

    Returns:
    A DataFrame representing the run list for the workflow map.
    """
    runlist = pd.DataFrame(
        columns=[
            "run_id",
            "short_names_in",
            "operation",
            "ref",
            "short_name_out",
            "notes",
        ]
    )
    for i, current_file in raw_files.iterrows():
        short_name = current_file["short_name"]
        ref = short_name + default_skeleton_ref_suffix
        runlist.loc[len(runlist)] = [
            i + 1,
            short_name,
            default_skeleton_operation_name,
            ref,
            short_name + skeleton_update_suffix,
            np.nan,
        ]
        complete_ref_tree(
            ref,
            workflow_map.keys(),
            workflow_dict,
            short_name,
            workflow_map,
            column_summaries,
        )
    return runlist


def _update_runlist(workflow_map, worksheets, workflow_dict, column_summaries):
    """
    Updates an existing run list in the workflow map for mapping and renaming operations.

    Parameters:
    - workflow_map: The workflow map containing the run list to be updated.
    - worksheets: A list of worksheet names in the workflow map.
    - workflow_dict: Dictionary containing DataFrames for each short name in the workflow.
    - column_summaries: Dictionary to store column summaries for each short name.
    """
    runlist = workflow_map["runlist"]
    runlist_skel = runlist[
        runlist.operation == default_skeleton_operation_name
    ].reset_index(drop=True)
    for i, current_file in runlist_skel.iterrows():
        short_name, ref = current_file["short_names_in"], current_file["ref"]
        if pd.isnull(ref):
            ref = short_name + default_skeleton_ref_suffix
            workflow_map["runlist"].loc[
                (workflow_map["runlist"].operation == default_skeleton_operation_name)
                & (workflow_map["runlist"].short_names_in == short_name),
                "ref",
            ] = ref
        complete_ref_tree(
            ref, worksheets, workflow_dict, short_name, workflow_map, column_summaries
        )


def _prepare_out_worksheet(workflow_map, worksheets):
    """
    Prepares the 'out' worksheet in the workflow map if it does not already exist.

    Parameters:
    - workflow_map: The workflow map to be updated.
    - worksheets: A list of worksheet names in the workflow map.
    """
    if "out" not in worksheets:
        out = pd.DataFrame(
            {
                "short_name": workflow_map["runlist"].short_name_out,
                "output_name": workflow_map["runlist"].short_name_out,
            }
        )
        workflow_map["out"] = out


def complete_ref_tree(
    ref: str,
    worksheets: list,
    workflow_dict: dict,
    short_name: str,
    workflow_map: dict,
    column_summaries: dict,
):
    """
    Completes the reference tree for a given reference within the workflow map, creating reference and mapref tables
    as needed and summarizing data for mapped columns.

    Parameters:
    - ref: The reference to complete within the workflow map.
    - worksheets: A list of existing worksheet names within the workflow map.
    - workflow_dict: Dictionary containing DataFrames for each short name in the workflow.
    - short_name: The short name of the DataFrame being processed.
    - workflow_map: The workflow map to be updated.
    - column_summaries: Dictionary to store column summaries for each short name.
    """
    if ref not in worksheets:
        ref_table = pd.DataFrame(columns=["old_name", "new_name", "mapref", "notes"])
        columns = workflow_dict[short_name].columns
        ref_table.old_name = columns
        workflow_map[ref] = ref_table
        summary_table = pd.DataFrame(index=range(skeleton_top_n_entries))
        for column in columns:
            summary_table[column] = (
                workflow_dict[short_name]
                .groupby(column)
                .size()
                .reset_index()
                .sort_values(by=0, ascending=False)
                .reset_index(drop=True)
                .head(skeleton_top_n_entries)[column]
            )

        column_summaries[short_name] = summary_table

    else:
        ref_table = workflow_map[ref]
        maps_needed = ref_table[["old_name", "mapref"]]
        maps_needed = maps_needed[pd.notnull(maps_needed.mapref)]
        mapref_dict = dict(zip(maps_needed.old_name, maps_needed.mapref))
        for k in mapref_dict.keys():

            if mapref_dict[k] not in worksheets:
                mapref_table = pd.DataFrame(columns=["old_value", "new_value", "notes"])
                mapref_table["old_value"] = (
                    workflow_dict[short_name]
                    .groupby(k)
                    .size()
                    .reset_index()
                    .sort_values(by=0, ascending=False)
                    .reset_index(drop=True)[k]
                )
                workflow_map[mapref_dict[k]] = mapref_table
