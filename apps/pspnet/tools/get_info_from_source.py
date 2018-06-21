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


service_name='CPHHS_Share'
def smb_conn():
  userID = 'guxi'
  password = 'cft6&UJM'
  client_machine_name = socket.gethostbyname('localhost')

  server_name = 'cphhs.tss.oregonstate.edu'
  
  server_ip = socket.gethostbyname('cphhs.tss.oregonstate.edu')

  domain_name = 'onid'


  conn = SMBConnection(userID, password, client_machine_name, server_name, domain=domain_name, #use_ntlm_v2=True,
                       is_direct_tcp=True)

  conn.connect(server_ip, 445)
  #Words =conn.echo("Hello Hello")
  #print(Words )
  return conn

tgt='result'
remote_path=[]
remote_path.append("BPHS\Restricted\SHL\\GSV_Data\\GSV_image_guxi\\result")

remote_path.append("BPHS\Restricted\SHL\Processed_Images\guxi_results")

conn=smb_conn()
count_rmt=0
rmdb=collections.defaultdict(lambda :False)

for rp in remote_path:
    remote_f_list_obj=conn.listPath(service_name,rp)
    for x in tqdm.tqdm(remote_f_list_obj):
        if not rmdb[os.path.splitext(x.filename)[0]]:
          rmdb[os.path.splitext(x.filename)[0]]=('smb',rp)
          count_rmt=count_rmt+1
        #remote_file_list={x.filename:x.file_size for x in remote_f_list_obj}
    print("\n\n\n\n{0}\n\n\n".format(count_rmt))
print(rmdb.keys()[1])

#************************************

db=pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
db2=pymysql.connect(host="23.95.18.57",port=3306, user="guxi",passwd="dHtFkI6g",db="gsv_file_list2")

# read panid list
ldb= collections.defaultdict(lambda :False)
sql1="select pid from tasks "
sql2="select panid from result_percent "
count=0
final_list=[]
with db.cursor() as cur:
  cur.execute(sql1)
  lines=cur.fetchall()
  db.commit()
  for l in tqdm.tqdm(lines):
    ldb[l[0]]=True
  cur.execute(sql2)
  lines2=cur.fetchall()
  for l2 in tqdm.tqdm(lines2):
     if not rmdb[l2[0]]:
       rmdb[l2[0]]=("db","db2")
       count_rmt=count_rmt+1


  with db2.cursor() as cur2:
      cur2.execute(sql2)
      lines3=cur2.fetchall()
      for l2 in tqdm.tqdm(lines3):
         if not rmdb[l2[0]]:
           rmdb[l2[0]]=("db","db2")
           count_rmt=count_rmt+1


  import json
  list=[]
  with open("undo_list_smb.txt",'r+') as f:
      j=f.read()
      list=json.loads(j)
  for item in list:
    final_list.append((item,rmdb[item]))

  with open("source_finder.txt",'w+') as f:
    f.write(json.dumps(final_list))
print("\n\n\ntotal={1}\nnot found={0}\n\n\n".format(count,count_rmt))
# read result list
# compare
# output