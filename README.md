# Flexible Load Analysis
Flexible Load Analysis is a Python package for loading, modelling and analysis of load-timeseries and net-data, with a focus on flexibility.  
The program was originally made to test load-modelling methods described in [Erling Tønne's Doctoral Thesis](http://hdl.handle.net/11250/2476389).  
The script is created by SINTEF Energi AS in conjunction with CINELDI WP1.

## Installation
The package is installed by cloning this repository to your own local machine.
Using the package requires the following dependencies:

### Dependencies
* Python 3
* [numpy](https://numpy.org/)
* [pandas](https://pandas.pydata.org/pandas-docs/stable/index.html#)
* [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
* [toml](https://toml.io/en/)
* [networkx](https://networkx.org/)
* [pandapower](https://www.pandapower.org/)

Install all dependencies by running  
```bash
python3 -m pip install -r requirements.txt
```

## Usage
The library can be used standalone with any of the included scripts.

More relevantly, however, is using the functionality for loading, data-structures and analyses in your own project as an included package. 
As of now, this is done by adding this repo as a git submodule into your own project, adding the packages' requirements into your own,
installing these and then importing the package like any other python package.

The library may be used as a Git submodule. In that case, remember to run
```bash
git submodule update --remote
```
to actually download and update the contents of the package.

To use the included scripts, create a fitting config-file to reflect placement and structure of your load-timeseries dataset, as well as changing any other relevant fields.

Required data-files and supported formats is described in example_data\TUTORIAL.md

After this, the included scripts may be ran by running
```bash
python3 -m scripts.interactive_FLA
```

See the source-code for how to implement custom preprocessing-steps as well as other models.

## Development
The project follows PEP8-styling and the numpydoc-standard 
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

Copyright &copy; 2021 SINTEF Energi AS