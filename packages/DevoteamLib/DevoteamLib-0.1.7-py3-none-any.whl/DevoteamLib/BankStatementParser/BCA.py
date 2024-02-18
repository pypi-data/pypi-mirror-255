import re
from datetime import datetime
import pandas as pd
import numpy as np

class BCA:
  def __init__(self):
    self.monthData = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.BCA_table_spliting(df)

  def BCA_Second_Check(self,text):
    new_text = []
    for i in text:
        if i in "1234567890.,DB ":
            new_text.append(i)
    return ''.join(new_text)

  def BCA_table_spliting(self,df):
      #retrieving first row to get the year
      first_row = df[0].upper()
      year = re.findall('PERIO\DE\s+.*?(\d{4})',first_row)[0]

      df = df[1]
      dtlist = {
          "INDEX":[],
          "BULAN_TAHUN":[],
          "TANGGAL":[],
          "KETERANGAN":[],
          "MUTASI":[],
          "SALDO":[],
          "CBG":[]
      }

      indexing = 0
      print(df)
      for er in df:
          try:
              stringnumdata = re.findall(r"(\d\d\/\d\d)\s+(.*)",er[0])[0]
              dtlist['INDEX'].append(indexing)
              indexing+=1
          except:
              print('Gagal Indexing:',stringnumdata)
              continue

          data = self.BCA_Second_Check(er[1]).strip().split(' ')
          date = stringnumdata[0].split("/")
          # print(stringnumdata)
          # print(er[1])
          # print(data)
          # print("============================\n")
          if '' in data:
              data.remove('')

          if 'DB' in data:
              index_db = data.index('DB')
              data[index_db-1]+=' '+data[index_db]
              data.remove('DB')

          data = [x.replace("B","") for x in data]

          if len(dtlist['SALDO'])==0:
              dtlist["CBG"].append("")
              dtlist["MUTASI"].append("")
              dtlist["SALDO"].append(data[0])
              dtlist['BULAN_TAHUN'].append("{0} {1}".format(self.monthData[int(stringnumdata[0].split('/')[1])-1], year))
              dtlist['KETERANGAN'].append(stringnumdata[1])
              dtlist['TANGGAL'].append(year+'-'+date[1]+'-'+date[0])
              continue
          if len(data)>=3:
              dtlist["CBG"].append(data[0])
              dtlist["MUTASI"].append(data[1])
              dtlist["SALDO"].append(data[2])
          elif len(data)==2:
              if len(data[0])==4:
                  dtlist["CBG"].append(data[0])
                  dtlist["MUTASI"].append(data[1])
                  dtlist["SALDO"].append("")
              else:
                  dtlist["CBG"].append("")
                  dtlist["MUTASI"].append(data[0])
                  dtlist["SALDO"].append(data[1])
          elif len(data)==1:
              dtlist["CBG"].append("")
              dtlist["MUTASI"].append(data[0])
              dtlist["SALDO"].append("")
          dtlist['BULAN_TAHUN'].append("{0} {1}".format(self.monthData[int(stringnumdata[0].split('/')[1])-1], year))
          dtlist['KETERANGAN'].append(stringnumdata[1])
          dtlist['TANGGAL'].append(year+'-'+date[1]+'-'+date[0])

          try:
            pd.DataFrame.from_dict(dtlist)
          except:
            print(data)
            input()

      # Table Cleanup
      print(dtlist)
      df = pd.DataFrame.from_dict(dtlist)
      print(df.info())
      # df = df.drop(df[df['MUTASI'].str.contains('\d') == False].index[0])
      df['STATUS'] = ['DEBIT' if 'D' in x else 'CREDIT' for x in df['MUTASI']]
      df['AMMOUNT'] = df['MUTASI'].str.replace('DB', '').str.replace('D', '').str.replace(',', '').str.replace(' ', '').str.replace('.', '').replace('', np.nan).astype(float)
      df['AMMOUNT'] = df['AMMOUNT'].apply(lambda x:x/100)
      df['SALDO'] = df['SALDO'].apply(lambda x: x.strip()).str.replace('D', '').replace('', np.nan)
      df['SALDO'] = df['SALDO'].str.replace(',', '').str.replace('.', '').str.replace(' ', '').astype(float)
      df['SALDO'] = df['SALDO'].apply(lambda x:x/100)

      return df[["INDEX","BULAN_TAHUN","TANGGAL", "KETERANGAN", "STATUS", "AMMOUNT", "SALDO"]]