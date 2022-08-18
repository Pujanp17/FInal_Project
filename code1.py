""" 
COMP 593 - Final Project

Description: 
  Downloads NASA's Astronomy Picture of the Day (APOD) from a specified date
  and sets it as the desktop background image.

Usage:
  python apod_desktop.py image_cache_path [apod_date]

Parameters:
  image_cache_path = Full path of the image cache directory
  apod_date = APOD date (format: YYYY-MM-DD)

History:
  Date        Author    Description
  2022-05-09  J.Dalby   Initial creation
"""
from os import path
from sys import argv, exit
from datetime import datetime, date
from hashlib import  sha256
from os import path, makedirs
from ctypes import windll
from pytest import param
import requests
import sqlite3
import re


def main():
    # *** DO NOT MODIFY THIS FUNCTION ***

    # Determine the path of image cache directory and SQLite data base file
    image_cache_path = get_image_cache_path()
    db_path = path.join(image_cache_path, 'apod_images.db')

    # Determine the date of the desired APOD
    apod_date = get_apod_date()

    # Create the image cache database, if it does not already exist
    create_apod_image_cache_db(db_path)

    # Get info about the APOD from the NASA API
    apod_info_dict = get_apod_info(apod_date)
    
    # Get the URL of the APOD
    image_url = get_apod_image_url(apod_info_dict)
    image_title = get_apod_image_title(apod_info_dict)
    
    # Determine the path at which the downloaded image would be saved 
    image_path = get_apod_image_path(image_cache_path, image_title, image_url)

    # Download the APOD image data, but do not save to disk
    image_data = download_image_from_url(image_url)

    # Determine the SHA-256 hash value and size of the APOD image data
    image_size = get_image_size(image_data)
    image_sha256 = get_image_sha256(image_data)

    # Print APOD image information
    print_apod_info(image_url, image_title, image_path, image_size, image_sha256)

    # Add image to cache if not already present
    if not apod_image_already_in_cache(db_path, image_sha256):
        save_image_file(image_data, image_path)
        add_apod_to_image_cache_db(db_path, image_title, image_path, image_size, image_sha256)

    # Set the desktop background image to the selected APOD
    set_desktop_background_image(image_path)

def get_image_cache_path():
    if len(argv) >= 2:
        dir_path = argv[1]

        if not path.isabs(dir_path):
            print('Error: Image cache path parameter must be absolute.')
            exit('Script execution aborted')
        else:
            if path.isdir(dir_path):
                print('Image cache directory:', dir_path)
                return dir_path
            elif path.isfile(dir_path):
                print ('Error: Path parameter is existing file.')
                exit('Script execution aborted')
            else:
                print("creating  new image directory '" + dir_path + "'...", end= '')
                try:
                    makedirs(dir_path)
                    print('success')
                except:
                    print('Failure')
                return dir_path

    else: 
        print('Error: Missing Image path parameter')
        exit('Script execution aborted')

def get_apod_date():

    if len(argv) >= 3:
        apod_date = argv[2]

        try:
            apod_datetime = datetime.strptime(apod_date, '%Y-%m-%d')
        except  ValueError:
            print('Error: Invalid date format YYYY-MM-DD')
            exit('Script aborted')

        if apod_datetime.date() < date(1995,6,16):
            print('Error: Date too far in the past ')
            exit('Script execution aborted ')
        elif apod_datetime.date() > date.today():
            print('Date cannot be in the future')
            exit ('Script execution aborted')
    else:
        apod_date = date.today().isoformat()

    print("APOD date:", apod_date)
    return apod_date

def get_apod_image_path(image_cache_path, image_title, image_url):

    file_ext = image_url.split(".")[-1]
    # Remove leading and trailing spaces from the title
    file_name = image_title.strip()
    # Replace inner spaces with underscores
    file_name = file_name.replace(' ', '_')

    # Remove any non-word characters
    file_name = re.sub(r'\W', '', file_name)

    # Append the extension to the file name
    file_name = '.'.join((file_name, file_ext))

    # Joint the directory path and file name to get the full path
    file_path = path.join(image_cache_path, file_name)

    return file_path

def get_apod_info(apod_date):

    print("Getting image Information from NASA... Please stand by...", end= '')

    NASA_API_KEY = 'tz6CvXkLfg4etTXfvIZSOFaGDi6Cmm9BT393j05V'
    APOD_URL = "https://api.nasa.gov/planetary/apod"
    apod_params = {
        'api_key' : NASA_API_KEY,
        'date' : apod_date,
        'thumds' : True
    }
    resp_msg = requests.get(APOD_URL, params=apod_params)

    if resp_msg.status_code == requests.codes.ok:
        print('success')
    else:
        print('Failure code', resp_msg.status_code)
        exit('script execution abort')

    apod_info_dict = resp_msg.json()
    return apod_info_dict

def get_apod_image_url(apod_info_dict):
    """
    Gets the URL of the APOD image from the dictionary of APOD information.
    If the APOD is a video, gets the URL of the video thumbnail. 

    :param apod_info_dict: Dictionary of APOD info
    :returns: APOD image URL
    """   
    return 'TODO'

def get_apod_image_title(apod_info_dict):
    """
    Gets the title of the APOD image from the dictionary of APOD information.

    :param apod_info_dict: Dictionary of APOD info
    :returns: APOD image title
    """   
    return 'TODO'

def print_apod_info(image_url, image_title, image_path, image_size, image_sha256):
    """
    Prints the following information about the APOD:
    - Image URL
    - Path at which image is saved in the image cache
    - Image size in bytes
    - Image SHA-256 hash value 

    :param image_url: URL of the APOD image
    :param image_title: Title of the APOD image
    :param image_path: Path of the APOD image file saved locally
    :param image_size: Size of APOD image in bytes
    :param image_sha256: SHA-256 hash value of APOD image
    :returns: None
    """    
    return #TODO

def create_apod_image_cache_db(db_path):
    """
    Creates the APOD image cache SQLite database if it 
    doesn't already exist.

    :param db_path: Path of APOD image cache .db file
    :returns: None
    """
    return #TODO

def add_apod_to_image_cache_db(db_path, image_title, image_path, image_size, image_sha256):
    """
    Adds a specified APOD image to the image cache database.

    :param db_path: Path of APOD image cache .db file
    :param image_title: Title of the APOD image
    :param image_path: Path of the APOD image file saved locally
    :param image_size: Size of APOD image in bytes
    :param image_sha256: SHA-256 hash value of APOD image
    :returns: None
    """
    return #TODO

def apod_image_already_in_cache(db_path, image_sha256):
    """
    Determines whether an image with a specified SHA-256 hash value
    is already present in the image cache.

    :param db_path: Path of APOD image cache .db file
    :param image_sha256: SHA-256 hash value of APOD image
    :returns: True if image is already in the cache; False otherwise
    """ 
    return False #TODO

def get_image_size(image_data):
    """
    Determines the size of an image in bytes

    :param image_data: Image data binary string
    :returns: Size of image in bytes
    """
    return 'TODO'

def get_image_sha256(image_data):
    """
    Calculates the SHA-256 hash value of an image

    :param image_data: Image data binary string
    :returns: SHA-256 hash value of image (hexadecimal string)
    """
    return 'TODO'

def download_image_from_url(image_url):
    """
    Downloads an image from a specified URL.
    ** DOES NOT SAVE THE IMAGE TO DISK **

    :param image_url: URL of image
    :returns: Image data binary string (content of response message)
    """
    return 'TODO'

def save_image_file(image_data, image_path):
    """
    Saves image data as a file on disk.
    ** DOES NOT DOWNLOAD THE IMAGE **

    :param image_data: Image data binary string
    :param image_path: Path to save image file
    :returns: None
    """
    return # TODO

def set_desktop_background_image(image_path):
    """
    Changes the desktop wallpaper to a specific image.

    :param image_path: Path of image file
    :returns: None
    """
    return # TODO

main()