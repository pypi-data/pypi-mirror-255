# Table of Contents
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Installation](#installation)
- [Upgrading](#upgrading)
- [Required data](#required-data)
- [Configuration (for calc\_pager\_event API usage and command line usage)](#configuration-for-calc_pager_event-api-usage-and-command-line-usage)
- [Command Line Usage](#command-line-usage)
- [Library Usage](#library-usage)

# Introduction

This library of tools forms the modeling core of the Prompt Assessment for Global Earthquake Response (PAGER) system,
which provides fatality and economic loss impact estimates following significant earthquakes worldwide. The models implemented here are based on work described in the following papers:

```
Jaiswal, K. S., and Wald, D. J. (2010). An Empirical Model for Global Earthquake Fatality Estimation. Earthquake Spectra, 26, No. 4, 1017-1037
```

```
Jaiswal, K. S., and Wald, D. J. (2011). Rapid estimation of the economic consequences of global earthquakes. U.S. Geological Survey Open-File Report 2011-1116, 47p.
```

```
Jaiswal, K. S., Wald, D. J., and D’Ayala, D. (2011). Developing Empirical Collapse Fragility Functions for Global Building Types. Earthquake Spectra, 27, No. 3, 775-795
```

The software here can be used for other applications, although it is important to note that the empirical loss models
have not been calibrated with events newer than 2010, and the semi-empirical fatality model results are less accurate than the empirical equivalent.

# Installation

`pip install esi-utils-pager`

# Upgrading

`pip install --upgrade esi-utils-pager`

# Required data

A number of data files external to the repository are required for usage:

 - Population grid, which can be obtained from Oakridge National Labs [Landscan project](https://landscan.ornl.gov/about)
 - Country code grid, which can be obtained upon request from the PAGER team.
 - Urban/rural code grid, obtained from the Socioeconomic Data and Applications Center [(SEDAC)](https://sedac.ciesin.columbia.edu/data/collection/grump-v1)

# Configuration (for calc_pager_event API usage and command line usage)
To run the `pagerlite` program (see below), you must first create a `.losspager/config.yml` file in your home directory. 
You can make the .losspager directory using this command (on Linux and Mac platforms):

`mkdir ~/.losspager`

You may then create the config.yml file in that directory using your text editor of choice. 
This file should look like the following: 

```
#############Minimum PAGER configuration################
#This is where output data goes
output_folder: /data/pagerdata/output/

#Anything not already captured by PAGER event logs will be written here
log_folder: /data/pagerdata/logs

#This section describes all the data needed to run models and make maps
model_data:
  timezones_file: /data/pagerdata/model_data/combined_shapefile.shp
  country_grid: /data/pagerdata/model_data/countriesISO_Aug2022_withbuffer.tif
  population_data:
  - {population_grid: /data/pagerdata/model_data/population/lspop2018.flt, population_year: 2018}
  urban_rural_grid: /data/pagerdata/model_data/glurextents.bil
```


# Command Line Usage
The command line program made available by this repository is `pagerlite`. This program outputs detailed empirical
(fatality/economic) PAGER model results to a tabular format. To see the help for this program:

`pagerlite -h`

There are three input modes for pagerlite:

 - `pagerlite -e <eventid>` Run pagerlite on a single event specified by a ComCat event ID.
 - `pagerlite -g <grid.xml>` Run pagerlite on a single grid.xml file.
 - `pagerlite -f <gridfolder>` Run pagerlite on a directory containing many grid.xml files 
    (these files can be in sub-directories).



# Library Usage

Usage of the relevant code modules is detailed in the Jupyter notebooks, most notably in the 
[Earthquake Losses notebook](https://code.usgs.gov/ghsc/esi/esi-utils-pager/-/blob/main/notebooks/EarthquakeLosses.ipynb)


