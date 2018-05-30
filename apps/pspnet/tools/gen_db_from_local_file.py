#load ignore list

#scan local files
scan_path="./"
from os import walk
import os

f = []
for (dirpath, dirnames, filenames) in walk(scan_path):
    for fn in filenames:
        if os.path.splitext(fn)[1]==".jpg":
            f.append(os.path.relpath(scan_path+'/'+dirpath+'/'+fn))
print(f)
#init connect

sql={
    "tasks":"INSERT INTO `gsv_file_list`.`tasks`(`pid`,`status`,`locker`,`info`)VALUES(\"{0}\",\"init\",\"\",\"\");",
    "files":"INSERT INTO `gsv_file_list`.`files`(`pid`,`path`,`resultpath`)VALUES(\"{0}\",\"{1}\",\"{2}\");"
}
#run inserts
