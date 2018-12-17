import sys 

sys.path.append('../../../')
import apps.streetdownloader.pkg.streetview as streetview

sys.path.append('/scratch/guxi/gsv_processor')
import urlsigner

import logging
import subprocess
import requests
import multiprocessing
import pandas as pd
import numpy as np
import sqlalchemy as sa
from tqdm import tqdm
import json
import contextlib
import traceback  
from collections import OrderedDict

def work_pp(args):
    """
    get lastest image in historial list which from google street view js api

    """
    try:
        #print(args)
        panoids,err = streetview.panoids(lat= args['lat'], lon= args['long'])
        sorted_panoids=sorted(panoids,key=lambda a:a['year']*12+a['month'])
        #print(sorted_panoids)
        if len(sorted_panoids)>=1:
            ret=sorted_panoids[-1]
              
        else:
            # try backup solution
            url="https://maps.googleapis.com/maps/api/streetview/metadata?location={0},{1}&size=640x640&key=AIzaSyC-VbDVpdam2nGKACnREqwN2M8moWn81XI".format(args['lat'],args['long'])
            url=urlsigner.sign_url(url,'')
            resp=requests.get(url, proxies=None)
            resp.encoding='utf-8'

            text=resp.text.encode('utf8')
        
            json_content=json.loads(text,object_pairs_hook=OrderedDict) 

            #exit()
            if (json_content['status']=='OK'):
              y,m=json_content['date'].split('-')

              ret={'lat': args['lat'], 'panoid': json_content['pano_id'], 'month': int(m), 'lon':  args['long'], 'year': int(y)}
            else:
              tqdm.write('{0} back up failed'.format(args['id']))
              ret={'lat': args['lat'], 'panoid': err, 'month': -1, 'lon':  args['long'], 'year': -1}
        ret['id']=args['id']
        return pd.Series(ret)
    except:
        print('**************************')
        traceback.print_exc() 
        return {'lat': args['lat'], 'panoid': 'unknown', 'month': -1, 'lon':  args['long'], 'year': -1,'id':args['id']}

def work(args):
    """
    using for parrllel later
    """
    return work_pp(args)

def main():
    
    print("db init....")
    #engine = sa.create_engine('mysql+pymysql://guxi:dHtFkI6g@127.0.0.1:33061/image')
    print("db fetch....")
    #df = pd.read_sql_query("select * from err_loc;", engine)
    df=pd.DataFrame(pd.read_csv('/scratch/guxi/gsv_processor/no_result_loc_info_all.csv'))
    print("appling....")
    a=[]
    with tqdm(df.iterrows(),total=len(df)) as pbar:
      for index,item in pbar:
        a.append(work(item))
    pd.DataFrame(a).to_csv('ret.csv')
if __name__ == '__main__':
    main()
