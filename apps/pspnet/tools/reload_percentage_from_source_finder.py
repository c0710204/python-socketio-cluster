# read source_finder
import pymysql
import json
import numpy as np
import tqdm
import smb
import os
import socket

from smb.SMBConnection import SMBConnection
#*****************************
db=pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")

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
#************************************
conn=smb_conn()
sql3='INSERT INTO result_percent(panid,info)VALUES("{0}","{1}");'
ignore=0
import sys
if len(sys.argv)>1:
    ignore=int(sys.argv[1])
with db.cursor() as cur:
  list=[]
  with open("source_finder.txt",'r+') as f:
    j=f.read()
    list=json.loads(j)
  
  for item in tqdm.tqdm(list):
      if ignore>0:
          ignore=ignore-1
          continue
      pid=item[0]
      type=item[1][0]
      p=item[1][1]
      if type=="smb":
          try:
              with open('./temp.npy','w+') as f:
                  conn.retrieveFile(service_name,"{0}/{1}.npy".format(p,pid),f)
              class_image=np.load('./temp.npy')
              l = [np.count_nonzero(class_image == i) for i in range(150)]
              info=json.dumps(l)
              os.remove("./temp.npy")
              cur.execute(sql3.format(pid,info))
              db.commit()
          except Exception as e:
              tqdm.tqdm.write("{0} failed:{1}!".format(pid,e))
              break
      else:
          tqdm.tqdm.write("{0} not smb!".format(pid))
