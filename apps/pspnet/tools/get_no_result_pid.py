# file => result check
# conn

import tqdm
import smb
import sys
import os
from smb.SMBConnection import SMBConnection
import socket

import pymysql
import collections
import tqdm

db=pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")

# read panid list
ldb= collections.defaultdict(lambda :False)
sql1="select pid from tasks "
sql2="select panid from result_percent "
count=0
count_rmt=0
final_list=[]
with db.cursor() as cur:
  cur.execute(sql2)
  lines=cur.fetchall()
  db.commit()
  for l in tqdm.tqdm(lines):
    ldb[l[0]]=True
  cur.execute(sql1)
  lines2=cur.fetchall()
  for l2 in tqdm.tqdm(lines2):
     count=count+1
     if not ldb[l2[0]]:
       final_list.append(l2[0])
       count_rmt=count_rmt+1

import json
with open("no_result_pid.txt",'w+') as f:
    f.write(json.dumps(final_list))
print("\n\n\ntotal={0}\nnot found={1}\n\n\n".format(count,count_rmt))
# read result list
# compare
# output