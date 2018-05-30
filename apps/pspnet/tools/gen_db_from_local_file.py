#load ignore list

#scan local files
scan_path="/scratch/guxi/googlestreeview_download/temp/DownloadedImages/"
from os import walk
import os

f = []
for (dirpath, dirnames, filenames) in walk(scan_path):
    for fn in filenames:
        if os.path.splitext(fn)[1]==".jpg":
            f.append(os.path.relpath(scan_path+'/'+dirpath+'/'+fn))
print(len(f))
#init connect
db=pymysql.connect(host="10.215.3.15",port=3306, user="guxi",passwd="dHtFkI6g",db="gsv_file_list")

sql={
    "tasks":"INSERT INTO `gsv_file_list`.`tasks`(`pid`,`status`,`locker`,`info`)VALUES(\"{0}\",\"init\",\"\",\"\");",
    "files":"INSERT INTO `gsv_file_list`.`files`(`pid`,`path`,`resultpath`)VALUES(\"{0}\",\"{1}\",\"{2}\");"
}
import tqdm
#run inserts
for fp in tqdm.tqdm(f):
    pass