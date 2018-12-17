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
db=mysqldb[0]

#check 1
# run get_no_result_pid.py
#check 2
# run 


with db.cursor() as cur:
  cur.execute("select status from tasks where status!=\"done\"")
  db.commit()
  lines=cur.fetchall()
  print(lines)