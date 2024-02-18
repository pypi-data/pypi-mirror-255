import re
from datetime import datetime
import pandas as pd

class BRI:
  def __init__(self):
    self.monthData = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.BRI_table_spliting(df)

  def BRI_table_spliting(self,df):
    for i in df:
      print("INFO",i)
    valBefore = float(re.findall(r"\d[\d\.,]+\d\d",df[2])[0].replace(",","").replace(".",""))/100

    df = df[1]
    # print(df[-1])
    dtlist = {
        "INDEX":[],
        "BULAN_TAHUN":[],
        "TANGGAL":[],
        "KETERANGAN":[],
        "STATUS":[],
        "AMMOUNT":[],
        "SALDO":[]
    }
    for index,er in enumerate(df):
        data = re.findall(r"(\d\d\/\d\d\/\d\d)\s+(\d\d:\d\d:\d\d)\s+(.*)",er[0])[0]
        tgl,bulan,tahun = data[0].split('/')

        dtlist['TANGGAL'].append(f"20{tahun}-{bulan}-{tgl}")
        dtlist['INDEX'].append(index+1)

        bulan       = self.monthData[int(bulan)-1]

        dtlist['BULAN_TAHUN'].append(bulan+' 20'+tahun)
        dtlist['KETERANGAN'].append(data[2])

        data = er[1].strip().split(' ')

        current = 0
        if float(data[0].replace(',','').replace('.','')) == 0:
            dtlist['STATUS'].append('CREDIT')
            current = float(data[1].replace(',','').replace('.',''))/100
            valBefore += current
        else:
            dtlist['STATUS'].append('DEBIT')
            current = float(data[0].replace(',','').replace('.',''))/100
            valBefore -= current

        dtlist['AMMOUNT'].append(current)
        dtlist['SALDO'].append(valBefore)

    df = pd.DataFrame.from_dict(dtlist)
    df['AMMOUNT'] = df['AMMOUNT'].astype(float)

    return df