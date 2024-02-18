# Tabular Data Management Tool (tdmt)

## Basics

The Tabular Data Management Tool (tdmt) is a command line Python app to quickly get an understanding of any table(s) of data and their relationships.

The app uses a specially formatted spreadsheet that allows the user to specify how to process tabular data.

When there is a need to perform multiple operations on several files, the advantage of a tabular method compared to processing data directly in Python is that the processing steps are clearly trackable on a single table. This makes it easy to follow what was done to which file, and which files were combined in what ways, and in which order. The absence of detailed Python code makes the progression of operations easy to follow.

As described below, skeleton mode helps the user to quickly build an understanding of what is in the data and iteratively builds out the template, suggesting helpful next steps in the processing.

The other benefit is a clear audit trail of all the operations. The app provides a runlog with date, time and run information.

## Installation
Either by cloning the repo on Gitlab or by running pip install tdmt

## Usage
If used by cloning this repo, run on the command line using python3 tdmt.py [your_spreadsheet_template_name] or python3 tdmt.py [your_spreadsheet_template_name].xlsx

If used by pip install, run on the command line using tdmt [your_spreadsheet_template_name] or tdmt [your_spreadsheet_template_name].xlsx

## Data
Input data files are stored in the input folder. Outputs are saved to the output folder. If the output folder does not exist, the app creates one.


## Runmodes
The app runs in two modes, determined by a variable called runmode on the setup tab: normal or skeleton.

# Getting started
The quickest way to understand how the app works is to follow along with an example. The example starts with a single file called skeleton1.xlsx. This file gets updated and renamed. Updated versions of the files are also provided.

## Skeleton mode
Skeleton mode is a useful way to get to grips with any new dataset(s), as demonstrated in the examples included. To see it in action, run the app with each of the files. The output files correspond to the input names: 

Run tdmt skeleton1.xlsx: Provide only the file names on the raw tab and the app generates skeleton1_summary.xlsx and skeleton1_skel.xlsx in the output folder.

skeleton1_summary.xlsx lists the top 1000 most frequent unique values in each column. skeleton1_skel.xlsx is an updated version of the original file skeleton1.xlsx, this time populated with a runlist with map_and_rename options for each of the input tables that were provided. The ref column has values d1_mr1 and d2_mr1 which link to tabs with the same names. On each tab the column names of the corresponding data files are shown in the old_name column. Add a new name in the new_name column where needed. If a categorical column needs to be remapped, provide a reference in the mapref column. 

To ilustrate how to build the skeleton file out even further, find the file skeleton1_skel.xlsx, copy it to the main directory and rename it skeleton2.xlsx. On the d2_mr1 tab, in the new_name column, put the name 'categorical_value' in the row where the old name is 'cat'. This will rename this column from cat to 'categorical_value'. Next, in the mapref column row, put a mapref called 'rf1' (any unique reference can be used). This will allow us to re-map the categorical values in the data column originally named cat.

Save the spreadsheet and run it using tdmt skeleton2.xlsx. Find and open skeleton2_skel.xlsx which now has a new tab called rf1. On it all the categorical values are listed. Add new categorical values in the new_value column, for example, for A use apple, B use bear, and so on. Save the template in the main directory as normal1.xlsx. 

## Normal mode
To get the normal1.xlsx template ready to process the data, flip the value of runmode on the setup tab from skeleton to normal. Now further operations can be added, for example merging and concatenating tables. Select the out tab, choose which of the available tables by short_name should be saved and choose appriate file names for them.

Run tdmt normal1.xlsx and inspect the output.

## License
MIT

## Project status
Maintained on an as-needed basis
