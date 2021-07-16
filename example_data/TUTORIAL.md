# How to use this directory
This folder contains examples of all the necessary files needed to run this program, and an explanaition of how to use them.

# Files
## config.toml
File containing configuration of the program runtime, such as which parts of the program to run. Important parameters such as path to your datafiles must be put in such a config-file, and referred to in main.py.
See ../config.toml

## load_data
The program requires measurements of the loads at each customer/load-point as seperate files stored in it's own directory.

If the load-measurements are stored in a single file, typically when exported from a database, data_splitting.py may be used together with an encoding to split the data-file into a directory based on customer ID's. More on encodings later.

Currently the program supports the following file-formats:
- Text (.txt)
- Excel (.xlsx, .xls, etc)

**Format-requirements:**

- Must contain one column/row of timestamps and one column/row of measured value.
- Filename must be the name you want the node in the network to take.
- Must be in supported file-format.

## temp_data
To perform temperature-correction of the loads, temperature-measurements are also required. These follow the same rules for formatting as load_data.

Since this requires computing the daily average temperature, a longer timespan is better.

**Format-requirements:**

- Must contain data for (at least) the same timespan as the load-data.

## network

Directory of non-encoded network-data on MATPOWER-format.

data_splitting.py will create a new directory with encoded ID's, for 

## encoding

To protect the privacy of the customer-data, both from load_data and network, the ID's are encoded to an arbritary format. 

encoding.xlsx is used by the functions in data_splitting.py to encode the ID's from load_data during splitting and to encode ID's from the network-directory.

**Format-requirements:**

- Must be .xlsx-file
- Must contain old_ID in first column, and the appropriate new_ID in the second column.