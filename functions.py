import pytz
import string
import random
import os.path
from config import config

local_tz = pytz.timezone('Asia/Kolkata')

#This dictionary will help us to get month number from month
month_dict = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


# function to convert GMT to IST
def convert_to_ist(gmt):

    local_dt = gmt.replace(tzinfo = pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def get_file_name(content_type):

    #random name generation
    file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))

    extension = ''

    if 'image/png' in content_type:
        extension = '.png'
    elif 'audio/aac' in content_type:
        extension = '.aac'
    elif 'text/csv' in content_type:
        extension = '.csv'
    elif 'application/epub+zip' in content_type:
        extension = '.epub'
    elif 'image/gif' in content_type:
        extension = '.gif'
    elif 'image/jpeg' in content_type:
        extension = '.jpg'
    elif 'audio/mpeg' in content_type:
        extension = '.mp3'
    elif 'image/mpeg' in content_type:
        extension = '.mpeg'
    elif 'application/pdf' in content_type:
        extension = '.pdf'
    elif 'application/vnd.ms-powerpoint' in content_type:
        extension = '.ppt'
    elif 'application/x-tar' in content_type:
        extension = '.tar'
    elif 'video/webm' in content_type:
        extension = '.webm'
    elif 'image/webp' in content_type:
        extension = '.webp'
    elif 'application/vnd.ms-excel' in content_type:
        extension = '.xls'
    elif 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
        extension = '.xlsx'
    elif 'application/xml' in content_type:
        extension = '.xml'

    return file_name + extension


def save_html_file(file_name, response_object):

    with open(os.path.join(config["save_location"], file_name + ".txt"), 'w', encoding="utf-8") as f:
        f.write(response_object.text)


def save_file(file_name, response_object):

    with open(os.path.join(config["save_location"], file_name), 'wb') as f:
        for chunk in response_object.iter_content():
            f.write(chunk)