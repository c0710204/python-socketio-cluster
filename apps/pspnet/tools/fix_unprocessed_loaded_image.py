import pymysql
db=pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")

sql="update tasks set status=\"wait\" where status=\"loaded\""
with db.cursor() as cur:
  cur.execute(sql)
  db.commit()
