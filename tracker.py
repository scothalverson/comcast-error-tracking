import mechanize
from bs4 import BeautifulSoup
import urllib.request
import http.cookiejar as cookielib
import json
import datetime
import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def getAccountAttributes():
    #read login details from file
    with open("login.txt") as f:
        auth = f.readlines()

    ret = {}

    for line in auth:
        line = line.strip().split()
        ret[line[0]] = line[1]

    return ret

def initBrowser(auth):
    #create browser context
    cj = cookielib.CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)
    #open LACDPU login page
    br.open("http://10.0.0.1/index.jst")
    br.select_form(nr=0)
    #set user/pass 
    br.form['username'] = auth['username']
    br.form['password'] = auth['password']
    #login
    br.submit()
    #return for use elsewhere
    return br

def getData():
    url = "http://10.0.0.1/network_setup.jst"
    #open URL
    br.open(url)
    #get the response
    data = (br.response().read())
    #convert to BS4 opbject
    soup = BeautifulSoup(data, 'lxml')
    #find the tables in the page
    table = soup.find_all('table')
    #store tables from page
    ds_table = table[0]
    us_table = table[1]
    cm_table = table[2]
    
    #get headers for the 3 tables, then parse the tables into nested arrays
    ds_headers = [th.text.strip() for th in ds_table.find_all('th')]
    ds_rows = []
    for row in ds_table.find_all('tr')[1:]:  
        cells = [td.text.strip() for td in row.find_all('td')]
        ds_rows.append(cells)
    
    us_headers = [th.text.strip() for th in us_table.find_all('th')]
    us_rows = []
    for row in us_table.find_all('tr')[1:]:  
        cells = [td.text.strip() for td in row.find_all('td')]
        us_rows.append(cells)
    
    cm_headers = [th.text.strip() for th in cm_table.find_all('th')]
    cm_rows = []
    for row in cm_table.find_all('tr')[1:]:  
        cells = [td.text.strip() for td in row.find_all('td')]
        cm_rows.append(cells)

    return [str(datetime.datetime.now()), ds_headers, ds_rows, us_headers, us_rows, cm_headers, cm_rows]


auth = getAccountAttributes()
br = initBrowser(auth)

old_uc_errors = 0
while(True):
    data = getData()

    uc_errors = sum([int(x) for x in data[-1][-1]])
    print(data[0],(len(data[-1][-1]) > 1), uc_errors, uc_errors - old_uc_errors)
    old_uc_errors = uc_errors
    with open("log.txt","w") as f:
        f.write(data[0] + ",")
        f.write(str(len(data[-1][-1]) > 1) + ",")
        f.write(str(uc_errors) + ",")
        f.write(str(uc_errors - old_uc_errors) + ",")
        f.write("\n") 
    time.sleep(30)
