import tqdm
import pymysql
db_source=pymysql.connect(host="23.95.18.57",port=3306, user="guxi",passwd="dHtFkI6g",db="gsv_file_list2")
db_target=pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
sql={
    "from":"select pid from tasks",
    "to":"update tasks set status=\"before\" where ({0}) and id>0"
}

#run inserts
batch=64
with db_source.cursor() as cur1:
 with db_target.cursor() as cur2:
  ret=cur1.execute(sql['from'])
  l=cur1.rowcount
  with tqdm.tqdm(total=l) as pbar:
    for i in range(0,l,batch):
      try:
        lines=cur1.fetchmany(batch)
        sqls=" or ".join([" pid=\"{0}\" ".format(l1[0]) for l1 in lines])
        sql_final=sql['to'].format(sqls)
        #print(sql_final)
#        pbar.update(1)
        pbar.update(batch)
        cur2.execute(sql_final)
        db_target.commit()
      except Exception as e:
          raise e
          print(e)
      
