import pymysql
import tqdm
mysqldb=[]
mysqldb.append(pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list"))
mysqldb.append(pymysql.connect(host="23.95.18.57",port=3306, user="guxi",passwd="dHtFkI6g",db="gsv_file_list2"))

target_db=pymysql.connect(host="127.0.0.1",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")
tgtcur=target_db.cursor()
sql1="SELECT panid,info FROM result_percent"
sql2='INSERT INTO result_percent2(panid,info)VALUES("{0}","{1}") ON DUPLICATE KEY UPDATE info="{1}";'
for db in mysqldb:
      with db.cursor() as cur:
        print("preparing request...")
        cur.execute(sql1)
        db.commit()
        print("downloading dataset...")

        dt=cur.fetchall()
        print("merging dataset...")
        
        with tqdm.tqdm(dt) as pbar:
          for line in pbar:
            pbar.set_description("{0}".format(line[0]))
            tgtcur.execute(sql2.format(line[0],line[1]))
            target_db.commit()