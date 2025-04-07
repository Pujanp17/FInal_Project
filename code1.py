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
  2022-05-09  Pujan.P   Initial creation
"""

from sys import argv, exit
from datetime import datetime, date
from hashlib import  sha256
from os import path, makedirs
from ctypes import windll

from pytest import param
import requests
import sqlite3
import re
import ctypes
import hashlib


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

    file_name = image_title.strip()

    file_name = file_name.replace(' ', '_')

    file_name = re.sub(r'\W', '', file_name)

    file_name = '.'.join((file_name, file_ext))

    file_path = path.join(image_cache_path, file_name)

    return file_path

def get_apod_info(apod_date):

    print("Getting image Information from NASA... Please stand by...", end= '')

    NASA_API_KEY = 'tz6CvXkLfg4etTXfvIZSOFaGDi6Cmm9BT393j05V'
    APOD_URL = "https://api.nasa.gov/planetary/apod"
    apod_params = {
        'api_key' : NASA_API_KEY,
        'date' : apod_date,
        'thumbs' : True

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

    if apod_info_dict['media_type'] == 'image':
        return apod_info_dict['hdurl']
    elif apod_info_dict['media_type']== 'video':
        return apod_info_dict['thumbnail_url']

def get_apod_image_title(apod_info_dict):

    return apod_info_dict['title']

def print_apod_info(image_url, image_title, image_path, image_size, image_sha256):

    print("Apdo information of the Image")
    print("image title", image_title)
    print("URL", image_url)
    print("Size",image_size)
    print("Hash Value", image_sha256)

def create_apod_image_cache_db(db_path):

    con = sqlite3.connect(db_path)
    createTableQuery = """
        CREATE TABLE IF NOT EXISTS image_cache (
            image_title VARCHAR(30),
            image_path TEXT,
            image_size INTEGER,
            image_sha256 VARCHAR(30)
        )
    """
    con.execute(createTableQuery)
    con.commit()
    con.close()

def add_apod_to_image_cache_db(db_path, image_title, image_path, image_size, image_sha256):

    con = sqlite3.connect(db_path)
    query = """
        INSERT INTO image_cache VALUES (
            !,!,!,!
        )
    """
    con.execute(query,(image_title, image_path, image_size, image_sha256))
    con.commit()
    return None

def apod_image_already_in_cache(db_path, image_sha256):

    con = sqlite3.connect(db_path)
    cacheCheckQuery = """
        SELECT * from image_cache where image_sha256 = ?
    """
    cursor = con.cursor()
    cursor.execute(cacheCheckQuery, (image_sha256,))
    result = cursor.fetchall()
    if(len(result) > 0):
        return True
    else :
        return False

def get_image_size(image_data):

    return len(image_data)

def get_image_sha256(image_data):

    return hashlib.sha256(image_data).hexdigest()

def download_image_from_url(image_url):

    print("Download image from NASA....", end='')

    resp_msg = requests.get(image_url)

    if resp_msg.status_code == requests.codes.ok:
        print("success")
        return resp_msg.content
    else:
        print('Failure code', resp_msg.status_code)
        exit('Script execution aborted')

def save_image_file(image_data, image_path):

    try:
        print("Saving image to file to cache .......", end='')
        with open(image_path, 'wb') as fp:
            fp.write(image_data)
            print('success')
    except:
        print("Failure")
        exit('Script aborted')


def set_desktop_background_image(image_path):

    ctypes.windll.user32.SystemParametersInfoW(20, 0,image_path, 0x3)
    return None

main()