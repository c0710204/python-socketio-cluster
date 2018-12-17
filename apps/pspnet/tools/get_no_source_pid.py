import tqdm
import smb
import sys
import os
from smb.SMBConnection import SMBConnection
import socket


if len(sys.argv)<3:
  print("\nscript local remote\n")
  exit()
local_path=sys.argv[1]
remote_path="BPHS\Restricted\SHL\Processed_Images\\{0}".format(sys.argv[2])

# get local file list
onlyfiles = [f for f in os.listdir(local_path) if os.path.isfile(os.path.join(local_path, f))]
print(len(onlyfiles))
# get remote file list

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

conn=smb_conn()
remote_f_list_obj=conn.listPath(service_name,remote_path)
print(len(remote_f_list_obj)-2)
remote_file_list={x.filename:x.file_size for x in remote_f_list_obj}
#remote_file_list=remote_file_list[2:]

# diff
diff=[]
for a in tqdm.tqdm(onlyfiles):
  if a not in remote_file_list:
    diff.append(a)
  else:
    s1=os.path.getsize(os.path.join(local_path, a))
    s2=remote_file_list[a]
    if s1!=s2:
      diff.append(a)
print(len(diff))    
#do upload
err_count=0
errm=""
with tqdm.tqdm(diff) as phar:
  for fpath in phar:
    with open(os.path.join(local_path, fpath),'r') as f:
      
      try:
        errm=""
        conn.storeFile(service_name,"{0}/{1}".format(remote_path,fpath),f)
        
      except Exception as e:
        errm="{0}".format(e)
        err_count=err_count+1
        conn=smb_conn()
      phar.set_description("{0} {1}".format(err_count,errm))
