# Flexible Load Analysis
Flexible Load Analysis is a Python script for modelling and analysis of load-timeseries and net-data, with a focus on flexibility.  
The program was originally made to test load-modelling methods described in [Erling Tønne's Doctoral Thesis](http://hdl.handle.net/11250/2476389).  
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

Install all dependencies by running  
```Powershell
python3 -m pip install -r requirements.txt
```

## Usage
To use this script, change config.toml to reflect placement and structure of your load-timeseries dataset, as well as changing any other relevant fields.
Remember to update the path of the config in main.py as well.

Required data-files and supported formats is described in example_data\TUTORIAL.md

After this, the program may be ran by running
```Bash
python src/main.py
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