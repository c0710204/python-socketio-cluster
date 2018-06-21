#!/bin/env python
import tqdm
import pymysql
import csv
import json
from time import sleep
from io import StringIO

import collections
#conn to db
mysqldb=[]
mysqldb.append(pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list"))
#mysqldb.append(pymysql.connect(host="23.95.18.57",port=3306, user="guxi",passwd="dHtFkI6g",db="gsv_file_list2"))
#run sql
sql="SELECT * FROM result_percent2"
"""
def yield_fetch(cur):
  a=True
  while a:
    #print("fetching...")
    a=cur.fetchone()
    yield a
"""  

with open('result.csv', 'w+') as csvfile:
  #spamwriter = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_MINIMAL)
  try:
    dt2={}
    for db in mysqldb:
      with db.cursor() as cur:
        print("preparing request...")
        cur.execute(sql)
        db.commit()
        print("downloading dataset...")

        dt=cur.fetchall()
        print("merging dataset...")
        

    print("outputing dataset...")
    with tqdm.tqdm(dt) as pbar:
      for line in pbar:
        if not(line):
          break
        #pbar.set_description("{0}".format(line[1]))
        #print("\n|{0}|".format(line[2]))
        obj=json.loads("{0}".format(line[2]))
        newobj=[float(x)/(640.0*640.0) for x in obj]
        target="\"{0}\", {1}\n".format(line[1],', '.join(str(x) for x in newobj))
        csvfile.write(target)
  except Exception as e:
    raise e
    pass
#pull by line
# insert to pd