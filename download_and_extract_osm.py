from datetime import date, datetime
import logging
import os
import subprocess
import time
import traceback

import requests
from requests.exceptions import HTTPError


### Check the `main` function to ensure the variables are configured properly for your needs! ###

# Set up a console and file logger. This code block sets up the Python logging module, then I simply
# overwrite the `print` function with the `logging.info` function. This logger will write to file and
# print to the console.
#
# Doing this globally means it's accessible in all functions.
log_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    'logs',
    f'run_log_{date.today()}_{int(time.time())}.log'
))

if log_path and not os.path.isdir(os.path.dirname(os.path.abspath(log_path))):
    os.makedirs(os.path.dirname(os.path.abspath(log_path)))
log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

if log_path:
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

logger.setLevel(level=logging.INFO)

print = logging.info


def print_and_call_command(command):
    print('Calling system command:\n {}'.format(' '.join(command)))
    subprocess.check_call(command)
    return True

def download_new_york_latest(url='https://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf',
                             download_directory=os.path.abspath(__file__),
                             verify_tls=True):

    print(f'\nMaking an HTTP request to New York Latest at url:\n {url}')

    response = requests.get(url, verify=verify_tls)

    if response.status_code == 200:
        if not os.path.exists(download_directory):
            print(f'\nCreating download directory : {download_directory}')
            os.makedirs(download_directory)

        download_file = os.path.join(
            download_directory,
            os.path.basename(url)
        )
        if os.path.exists(download_file):
            print(f'\nDownload file exists. Overwriting file:\n {download_file}')
            os.remove(download_file)

        print(f'\nSaving file as:\n {download_file}')
        with open(download_file, 'wb') as osm_file:
            osm_file.write(response.content)

        return download_file
    else:
        print(f'\nAn error was encountered with status code {response.status_code}')
        try:
            response.raise_for_status()
        except HTTPError as http_error:
            print(f'HTTP error:\n {http_error}')
        except Exception as exc:
            print(f'A Python error has occurred : {exc}')

        return False

def filter_osm_roadways(osm_pbf_file, osmconvert_binary, osmfilter_binary,
                        extract_directory=os.path.abspath(__file__)):
    if not os.path.exists(extract_directory):
        print('\nCreating working directory:\n {}'.format(extract_directory))
        os.makedirs(extract_directory)

    print('\nConverting OSM protocol buffer formatted file to O5M to prep for filtering:')
    o5m_file = os.path.join(
        extract_directory,
        os.path.basename(osm_pbf_file).split('.')[0] + '.o5m'
    )
    print(f' {o5m_file}')

    if os.path.exists(o5m_file):
        print(f' File exists. Deleting:\n  {o5m_file}')
        os.remove(o5m_file)

    convert_parameters = [
        osmconvert_binary,
        osm_pbf_file,
        f'-o={o5m_file}',
    ]
    print_and_call_command(convert_parameters)

    print('\nFiltering out the OpenStreetMap roadways:')
    filtered_file = os.path.join(
        extract_directory,
        os.path.basename(osm_pbf_file).split('.')[0]+'_roadways.osm'
    )
    print(f' {filtered_file}')
    temporary_file = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'osmfilter_tempfile'
    ))
    filter_parameters = [
        osmfilter_binary,
        o5m_file,
        '--keep=highway=',
        (
            '--drop=highway=footway highway=pedestrian ' +
            'highway=path highway=track highway=steps highway=cycleway ' +
            'highway=bridleway access=private highway=raceway ' +
            'highway=abandoned construction=footway access=private'
        ),
        f'-o={filtered_file}',
        f'-t={temporary_file}',
        '--verbose'
    ]
    print_and_call_command(filter_parameters)

    return filtered_file

def osm_to_shapefiles(osm_filepath, output_directory, output_name='OpenStreetMap_Roadways'):
    layer_names = [
        'points',
        'lines',
        'multilinestrings',
        'multipolygons',
        'other_relations',
    ]
    print(f'\nExtracting OSM layers as shapefiles')
    if not os.path.exists(output_directory):
        print('Creating output directory:\n {}'.format(output_directory))
        os.makedirs(output_directory)

    for layer in layer_names:
        print(f'Working on layer: {layer}')
        output_shapefile = os.path.join(
            output_directory,
            f'{output_name}_{layer}.shp'
        )

        if os.path.exists(output_shapefile):
            print(f'File exists. Removing: {output_shapefile}')
            os.remove(output_shapefile)

        print(f'Saving as: {output_shapefile}')
        ogr2ogr_parameters = [
            'ogr2ogr',
            '-f', 'ESRI Shapefile',
            output_shapefile,
            osm_filepath,
            layer,
        ]
        try:
            print_and_call_command(ogr2ogr_parameters)
        except Exception as exc:
            message = f'EXCEPTION: There was an exception on the {layer} layer. Skipping.'
            if logger:
                logger.exception(message)
            else:
                print(message)
            pass
        print('')

    return True


def main():
    # Update the variables to meet your needs prior to running this script
    data_url = 'https://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf'
    verify_tls = False
    base_output_dir = r'P:\GIS\HighwayData\OpenStreetMap'

    output_shapefile_dir = os.path.join(
        base_output_dir,
        str(date.today())
    )

    if not os.path.isdir(base_output_dir):
        output_shapefile_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            'OpenStreetMap_Data',
            str(date.today())
        ))

    download_directory = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'osm_downloads',
        str(date.today())
    ))
    extract_directory = os.path.join(
        os.path.dirname(os.path.dirname(download_directory)),
        'extract',
        str(date.today())
    )

    download_file = download_new_york_latest(
        url=data_url,
        download_directory=download_directory,
        verify_tls=verify_tls
    )

    if not download_file:
        print(f'Something went wrong with the download:\n {download_file}')
        raise SystemExit('Raising system exit. Goodbye.')

    osmconvert_binary = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'bin',
        'osmconvert64-0.8.8p.exe'
    ))
    osmfilter_binary = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        'bin',
        'osmfilter.exe'
    ))

    filtered_osm_file = filter_osm_roadways(
        download_file,
        osmconvert_binary,
        osmfilter_binary,
        extract_directory=extract_directory,
    )

    osm_to_shapefiles(
        filtered_osm_file,
        output_shapefile_dir,
    )
    return True

if __name__ == '__main__':
    start_time = datetime.now()
    print(f'Starting script : {os.path.abspath(__file__)}')
    print(f'Start time      : {start_time}\n')

    try:
        main()
    except Exception as exc:
        if logger:
            logger.exception(f'An Exception occurred: {exc}: {traceback.format_exc()}')
        else:
            print(f'An Exception occurred: {exc}: {traceback.format_exc()}')
        raise exc


    end_time = datetime.now()
    print(f'Execution completed : {end_time}')
    print(f'Execution time      : {end_time-start_time}')
