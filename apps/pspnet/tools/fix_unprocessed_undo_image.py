import pymysql
import json
import tqdm
db=pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")

sql="update tasks set status=\"wait\" where pid=\"{0}\""
with db.cursor() as cur:
  list=[]
  with open("no_result_pid.txt",'r+') as f:
    j=f.read()
    list=json.loads(j)
  for pid in tqdm.tqdm(list):
      cur.execute(sql.format(pid))
      db.commit()
