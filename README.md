# Stochastic Load Analysis

Stochastic Load Analysis is a Python script for performing load modelling,
with a focus on the method described in 
[Erling Tønne's Doctoral Thesis](http://hdl.handle.net/11250/2476389). 
The script is created by SINTEF Energi AS in conjunction with CINELDI WP1.

## Installation

The script is installed by cloning this repository to your own local machine.
Running the script requires the following dependencies:

### Dependencies
* Python 3
* [numpy](https://numpy.org/)
* [pandas](https://pandas.pydata.org/pandas-docs/stable/index.html#)
* [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
* [toml](https://toml.io/en/)
* [networkx](https://networkx.org/)
* [pandapower](https://www.pandapower.org/)

## Usage

To use this script, change config.toml to reflect placement and structure of
dataset, as well as changing any other fields.
Remember to update the path of the config in main.py as well.

Which data-files the program requires is described in example_data\TUTORIAL.md

After this, the program may be ran by running
```Bash
python main.py
```

See the source-code for how to implement custom preprocessing-steps as well
as other models.

## Development
Development follows issues reported at the project's 
[Jira](https://jira.code.sintef.no/projects/CINELDI/summary).

The project follows PEP8-styling and numpy 
[docstring-styling](https://numpydoc.readthedocs.io/en/latest/format.html).

## License
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Authors
Contributors: Eirik Haugen, Daniel Bjerkehagen, Iver Bakken Sperstad, Susanne Sandell

Copyright (C) 2021 SINTEF Energi AS