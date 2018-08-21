#load ignore list

#scan local files
# scan_path='../'
scan_path="/home/ibm/guxi/images/"
from os import walk
import os

f = []
import tqdm
import pymysql
for (dirpath, dirnames, filenames) in tqdm.tqdm(walk(scan_path)):
    for fn in tqdm.tqdm(filenames):
        if os.path.splitext(fn)[1]==".jpg":
            f.append(os.path.abspath(dirpath+'/'+fn))
# print(f)
# exit()
#init connect
db=pymysql.connect(host="star.eecs.oregonstate.edu",port=33061, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")

sql={
    "tasks":"INSERT INTO `gsv_file_list`.`tasks`(`pid`,`status`,`locker`)VALUES(\"{0}\",\"init\",\"-1\");",
    "files":"INSERT INTO `gsv_file_list`.`files`(`pid`,`path`,`resultpath`)VALUES(\"{0}\",\"{1}\",\"{2}\");"
}

#run inserts
with db.cursor() as cur:
    for fp in tqdm.tqdm(f):
        panid=os.path.basename(fp)[:-4]
        # print("|{0}|{1}|\n".format(fp,panid))
        # exit()
        try:    
            cur.execute(sql['files'].format(panid,fp,"/home/ibm/guxi/result/"))
            db.commit()
        except Exception as e:
            tqdm.tqdm.write("{0}".format(e))
        try:    
            cur.execute(sql['tasks'].format(panid))
            db.commit()
        except Exception as e:
            tqdm.tqdm.write("{0}".format(e))            
