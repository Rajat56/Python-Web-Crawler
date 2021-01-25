import requests
import pymongo
import re
import string
import random
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime as dt
from datetime import timedelta as td
from bs4 import BeautifulSoup as bsoup
from config import config
from logger import logger
from time import sleep
from tld import get_tld
from functions import convert_to_ist, save_file, save_html_file, get_file_name, month_dict

# function to get link from tag, and then update database (will run in a loop)
def get_link(tag, mycol, document):

    url = tag.get('href')
    flag = 0                                                       # flag sort of acts like continue statement; if flag is 1, the subsequent statements are not executed

    if(url):
        valid_link = re.findall('^http.*|^/.*', url)               # link is valid if it starts from 'http' or starts with '/' (relative link)

    # get link parameters/table columns
    if valid_link:                                                 # continue only if valid_link is not empty

        link = valid_link.pop(0)

        if not link.startswith('http'):                            # if link is not absolute add root url to it

            if document["Link"][-1] == '/':
                link = link[1:]                                    # to avoid 2 consecutive '/' signs

            domain = get_tld(document["Link"], as_object=True).fld

            link = domain + link

        if mycol.count_documents({'Link': link}, limit=1) != 0:             # check if link is already present
            flag = 1

        if not flag:
            '''get date parameters - year, month, day, hour, min and seconds using
                response headers and the regex library'''
            requests_head = requests.head(link, allow_redirects=True)

            datetime = requests_head.headers['date']

            datetime = datetime.split()                                     # Before splitting, date is in this format:- Mon, 24 Aug 2020 14:18:38 GMT

            time = re.findall('[0-9]+', datetime[4])                        # datetime[4] contains time in the format hour:minutes:seconds

            time_params = {"year": int(datetime[3]),
                            "month": int(month_dict[datetime[2]]),          # month_dict helps us to convert name of month from three letter string to month number
                            "day": int(datetime[1]),
                            "hour": int(time[0]),
                            "mins": int(time[1]),
                            "sec": int(time[2])}

            utc_time = dt(time_params['year'], time_params['month'], time_params['day'], time_params['hour'], time_params['mins'], time_params['sec'])

            source_link = document['Link']

            is_crawled = False                                                      # initially link won't be crawled

            last_crawled_date = 0

            response_status = requests_head.status_code

            try:
                content_type = requests_head.headers['content-type']
            except:
                flag = 1

            if not flag:
                content_length = len(requests.get(link, allow_redirects=True).content)

                file_path = './HTML Files'

                created_at = convert_to_ist(utc_time)

                link_params = {"Link": link, "Source_Link": source_link, "Is_Crawled": is_crawled, "Last_Crawled_Dt": last_crawled_date, "Response_Status": response_status,
                                "Content_Type": content_type, "Content_Length": content_length, "File_Path": file_path, "Created_At": created_at}

                # insert document in collection
                x = mycol.insert_one(link_params)
                print(link_params["Link"])


# main crawling function
def crawl():

    # Create mongodb database and collection(table)
    myclient = pymongo.MongoClient(config['mongo_uri'])
    mydb = myclient[config["database_name"]]
    mycol = mydb[config["collection_name"]]
    # initialize cycle
    cycle = 1

    while True:

        time_before_24hrs = dt.now() - td(days=config["link_refresh_time"])             # This was the time 24 hours before this current time

        # Check collection for links that were either never crawled or were crawled more than 24 hours ago
        crawlable_documents = mycol.find( {'$or': [ {"Is_Crawled": False  }, {"Last_Crawled_Dt": {'$lt': time_before_24hrs} } ] } )

        print("Size of all docs = ", mycol.count_documents({}))
        print("Size of crawlable docs = ", mycol.count_documents({'$or': [ {"Is_Crawled": False }, {"Last Crawled_Dt": {'$lt': time_before_24hrs} } ]}))

        for document in crawlable_documents:

            requests_head = requests.head(document["Link"], allow_redirects=True)
            requests_get =  requests.get(document['Link'])

            response_status = requests_head.status_code
            content_type = requests_head.headers['content-type']

            if response_status != 200:

                mycol.update_one({'_id': document['_id']}, {'$set': {"Is_Crawled": True, "Last_Crawled_Dt": dt.now() } } )
                continue

            if 'text/html' not in content_type:

                # give appropriate name and save file
                r = requests_get
                file_name = get_file_name(content_type)
                save_file(file_name, r)

                mycol.update_one({ '_id' : document['_id']}, {'$set': {"Is_Crawled": True, "Last_Crawled_Dt": dt.now() } } )
                continue

            try:
                logger.debug("Making HTTP GET request: " + document['Link'])
                r = requests_get
                res = r.text
                logger.debug("Got HTML source, content length = " + str(len(res)))
            except:
                logger.exception("Failed to get HTML source from " + document['Link'])
                continue

            mycol.update_one({ '_id' : document['_id']}, {'$set': {"Is_Crawled": True, "Last_Crawled_Dt": dt.now() } } )

            # Generate string of random characters
            file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8))

            # Save html file to disc in a folder named HTML files
            save_html_file(file_name, r)

            logger.debug("Extracting links from the HTML")

            soup = bsoup(res, 'html.parser')

            tags = soup('a')

            if len(tags) == 0:
                continue

            # With multithreading crawl each link in tag
            with ThreadPoolExecutor(max_workers=5) as executor:

                for tag in tags:
                    executor.submit(get_link, tag, mycol, document)

            # print number of links crawled for reference
            print("Number of links crawled = ", mycol.count_documents({}))

            # check if maximum link limited is exceeded, 5000 in this case
            if mycol.count_documents({}) >= config["max_links"]:
                print('Maximum limit of links reached')

            '''end of cycle, sleep for 5 seconds'''
            print("Number of links crawled = ", mycol.count_documents({}))
            print("End of Cycle " + str(cycle) + ", sleeping for " + str(config["sleep_time"]) + " secs\n")
            sleep(config["sleep_time"])

            if mycol.count_documents({}) == 1:
                print("No links left to crawl")

            # Increment cycle
            cycle += 1
            print("Start of cycle " + str(cycle) + '\n')


if __name__ == "__main__":

    logger.debug('Starting process')

    logger.debug('Getting links in database')

    while True:
        try:
            crawl()
        except:
            print("Network Error occurred / No internet connection")
        sleep(0.2)


    logger.debug('Process complete')