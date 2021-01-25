# Python-Web-Crawler
Spiderbot - A Web Crawler
This is the code for crawling any website of your choice, in this case https://letterboxd.com. Links will be crawled recursively and stored in MongoDB database (database name is given in config.py file). In config.py file, various user parameters are given. Maximum link limit is set to 5000 and sleep time set to 5 seconds. You can edit these default parameters according to your crawling needs.

The root url will have to be entered manually in the MongoDB database, in the form of a json object with the relevant fields. You can change "Link" key according to your choice of url.

Example of root url:-
{"Link" : "https://letterboxd.com",

"Source_Link" : "",

"Is_Crawled" : false,

"Last_Crawled_Dt" : null,

"Response_Status" : 0,

"Content_Type" : "",

"Content_Length" : 0,

"File_Path" : "",

"Created_At" : ISODate("2020-08-29T12:46:00.000Z")}
Run locally from command line
First download and install MongoDB and a GUI tool of your choice (Robo 3T is a good option)

Install virtual environment first

   pip install virtualenv
Set up virtual environment with name myproject
   virtualenv myproject
Activate virtual environment
   (Linux) $ source myproject/bin/activate


   (Windows) > myproject\Scripts\activate
Install dependencies
   pip install -r requirements.txt
To start crawling process
    python3 crawler.py
