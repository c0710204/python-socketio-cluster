import tqdm
import pymysql
db_source=pymysql.connect(host="127.0.0.1",port=33060, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
db_target=pymysql.connect(host="10.215.3.15",port=3306, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
sql={
    "from":"select pid from tasks"
    "to":"update tasks set status=\"before\" where pid=\"{0}\" and id>0"
}

#run inserts
with db_source.cursor() as cur1:
 with db_target.cursor() as cur2:
  ret=cur1.execute(sql['from'])
  l=cur1.rowcount()
  for i in tqdm.trange(l):
      try:
            line=cur1.fetchone()
            cur2.execute(sql['to'].format(line[0]))
            db_target.commit()
      except Exception as e:
          print(e)
      