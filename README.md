# About This Project

This Python script and included binaries will download OSM data from the Geofabrik servers,
filter the data to include features that are tagged as a highway, and saves the highways 
as shapefiles for use with any GIS software.

## OpenStreetMap Data and Filtering

This directory contains data from the OpenStreetMap project: https://openstreetmap.org

OpenStreetMap is a GIS datasource that is constructed by a "community of mappers that contribute
and maintain data about roads, trails, cafes, railway stations, and much more" [(Source: About OSM)](https://www.openstreetmap.org/about).
The data is "Open", in that anyone can edit or download the data for their use.

This directory contains a weekly extract of OpenStreetMap data for New York State, which is sourced from here:
https://download.geofabrik.de/north-america/us/new-york.html

The `new-york-latest.osm.pbf` from the above link contains all of New York State's OpenStreetMap data, which 
includes everything you see on the map. To limit the size of the data in these directories, the data is filtered 
to the most commonly used GIS data source at DOTs - the roads.

OSM uses a key/value pair to tag attributes to each roadway. The OSM download is filtered to include all
data that are tagged with a "highway" key. From there, the following values are removed to help focus
the data on the public roadway network:

- footway
- pedestrian
- path
- track
- steps
- cycleway
- bridleway
- private
- raceway
- abandoned

The OSM data comes with multiple "layers", which include different shape types. The most relevant data 
will be the data that includes the suffix "_lines.shp" on the shapefiles, as these are where most of the roadways
are. All of the layers are unpacked and saved to the directory, so you can get a taste of what else is potentially available.

OpenStreetMap data changes frequently, and often times the accuracy can be questionable. Please be very considerate
when attempting to draw conclusions from this data. OpenStreetMap and the data providers are not responsible for errors or omissions.
We think of this mostly as a cartographic data source, but many individuals and companies (including the Fortune 500)
have had great success extracting value from OSM data.


# Technical Documentation
## Python Setup

The script is written in Python 3.6+ syntax. The easiest way to run this tool is using the Anaconda package distributor:
https://anaconda.org/anaconda
The original script was authored using miniconda. Conda installs Python packages and their Operating System dependencies, simplifying
the process of getting things like GDAL, NumPy, and Pandas running on your machine. The conda environment can be frozen
so that it's easily replicated on other machines.

The `environment.yml` file in this directory can be used to reconstruct the Python execution environment of this tool.
To recreate the environment, install Miniconda or Anaconda with Python 3.6+ and run the following two command:

```bash
conda upgrade conda
conda env create -f environment.yml
```

Conda should proceed to install the required packages. You can find more information regarding conda environments here:
https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html

## OSM Tools Setup

### OSM Tools Install Note

You will find the OSM Convert and OSM Filter binaries predownloaded for windows 64-bit in the `./bin` directory. 
If you leave them in place (an you're using 64-bit Windows!!) and do not
move the `download_and_extract_osm.py` script from the root directory, the binaries should be discovered by the script
without additional work.

### OSM Convert
This script relies on two open source tools distributed by OSM contributors. The tools are OSM Convert and OSM Filter.
There are binary files that can be downloaded from the web for 64 bit windows, which are the easiest way to get 
things running. OSM Convert is a utility that can convert OpenStreetMap data to and from various file formats. The
data is downloaded in Protocol Buffer Format, which is a compressed version of the OSM XML file. The 
download_and_extract_osm.py script will use this utility to convert the download from .pbf to the .o5m format.
This step is required for OSM Filter to execute. OSM Filter is optimized for the o5m format.

To install OSM Convert, go to this link:
https://wiki.openstreetmap.org/wiki/Osmconvert (or use the version included in the `./bin` directory of this repository).

Once you have downloaded the file, update the `download_and_extract_osm.py` file to point to the `osmconvert.exe` binary.
Python will then manage the execution of the tool.

### OSM Filter

OSM Filter is a utility that can be used to extract data of interest from the full OSM file. OSM data includes every single
thing that's visible on the map, from the traffic lights to the building polygons. Using OSM Filter, we can read the data from
NYS and find the data that is tagged with transportation related key/value pairs. See the ABOUT THIS PROJECT section of the README
for more information on what data are excluded by this script.

To install OSM Filter, go to this link:
https://wiki.openstreetmap.org/wiki/Osmfilter (or use the version included in the `./bin` directory of this repository).

Once you have downloaded the file, update the `download_and_extract_osm.py` file to point to the `osmfilter.exe` binary.
Python will then manage the execution of the tool.


## Scheduling Script Execution

This directory contains a Windows batch file, which can be used in the Windows Task Scheduler to schedule 
reoccuring updates of the OpenStreetMap data. The file is called `download_and_extract_osm_schedule.bat`
The .bat file simply activates the conda environment, runs the python script, and deactivates the conda env.

Once you have replicated the conda environment, you'll need to update the `download_and_extract_osm_schedule.bat`
script to point to the correct conda environment. If you navigate to the folder where you installed conda,
you'll find a folder called `condabin` which includes a file called `activate.bat`. Replace any call to `conda`
you may find in the batch file with the full filepath to the activate script. If you use the full path, you
can get around adding conda to your system path variable. It's best to leave Python 3 off of the conda path at this
time, since we are still using ArcGIS Desktop which relies on the deprecated Python 2. YMMV.

Once you have installed Conda and updated the path in the batch file, ensure you change line 2 of 
`downlaod_and_extract_osm_scheduled.bat` to match the location of the `download_and_extract_osm.py` on the system
you'll be using to run the script.

To actually schedule the job, simply go to the Windoze task Scheuduler and "Add a Task". You can set the frequency
to whatever you desire. Make sure the "Action" is to execute the `download_and_extract_osm_schedule.bat` script.

NOTE: I'd highly recommend ensuring that the script can be executed from a terminal window prior to scheduling the job.
The Windows Task Scheduler can be a bit difficult to debug, as the terminal window will disappear quickly. You can 
set the `timeout 5` line in the `download_and_extract_osm_schedule.bat` script to a bigger number (e.g. 3600 seconds)
to work around the quick-to-close problem.

## VS Code

If using VS Code, ensure that you update the settings.json file (found in `./.vscode/settings.json`) with the Anaconda
Python executable for your system. It's currently set to:
`D:\Program_Files\miniconda3\envs\py3\python.exe`

The VS Code settings are currently using Bandit linting. You can easily change that if you'd like.
