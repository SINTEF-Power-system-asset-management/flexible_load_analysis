# Flexible Load Analysis
Flexible Load Analysis (FLANLAN – FLexible (loading, storing and) ANalysis of Load And Net-data-correspondences) is a code platform implemented in Python. It performs loading, parsing, managing, anonymization, preprocessing, modification and analysis of mass load and grid data. Load analysis functionalities currently implemented include 
* a stochastic load model (based on http://hdl.handle.net/11250/2476389), 
* time series analysis to characterize the need for flexibility in the grid area, and
* "what-if" (or scenario) analyses to study the effects of grid connection of potential new loads with a certain load behaviour

The application of the code platform for characterizing the need for flexibility in an industrial distribution grid is demonstrated in a paper available as a preprint at https://doi.org/10.36227/techrxiv.20219964.

The code is developed by SINTEF Energi AS in conjunction with CINELDI WP1.

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
To use this script, change config.toml to reflect placement and structure of your load time series dataset, as well as changing any other relevant fields.
Remember to update the path of the config in main.py as well.

Required data-files and supported formats is described in example_data\TUTORIAL.md

After this, the program may be run by running
```Bash
python src/main.py
```

See the source code for how to implement custom preprocessing steps as well as other models.

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
Contributors: Daniel Bjerkehagen, Susanne Sandell, Eirik Haugen, Iver Bakken Sperstad

## Funding
This work has been funded by CINELDI – Centre for intelligent electricity distribution, an 8-year Research Centre under the FME scheme (Centre for Environment-friendly Energy Research, 257626/E20) of the Norwegian Research Council.

Copyright &copy; 2022 SINTEF Energi AS