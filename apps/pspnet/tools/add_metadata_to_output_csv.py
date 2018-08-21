#read metadata
#process csv by line
with open("result.csv",'r+') as csv:
  with open("result_meat",'w+') as csv_out:
    line=csv.readline();
    # get panid
    # search for metadata
    # output to output
