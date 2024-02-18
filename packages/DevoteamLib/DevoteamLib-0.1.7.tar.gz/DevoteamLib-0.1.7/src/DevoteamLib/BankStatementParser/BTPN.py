import re
from datetime import datetime
import pandas as pd
import numpy as np

class BTPN:
  def __init__(self):
    self.monthData = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.BTPN_table_spliting(df)

  def BTPN_table_spliting(self,df):
    sufix         = df[2]
    df            = df[1]
    dtlist        = []

    for index,er in enumerate(df):
      tanggal       = None
      keterangan    = None
      ammount       = None
      status        = None

      tanggal       = re.findall('(\d\d\/\d\d\/\d{4})',er[0])[0]
      print(tanggal)
      keterangan    = er[0].replace(tanggal,'').strip()

      tanggal       = tanggal.split('/')
      bulan_tahun   = f"{self.monthData[int(tanggal[1])-1]} {tanggal[2]}"

      tanggal       = f"{tanggal[2]}-{tanggal[1]}-{tanggal[0]}"

      uang_kas      = er[1].replace(",","").replace(".","").replace("IDR","").strip()

      if "_CREDIT" in uang_kas:
        status    = 'CREDIT'
        uang_kas  = uang_kas.replace('_CREDIT','')
      else:
        status = 'DEBIT'

      ammount = float(uang_kas)/100

      dtlist.append({
        'INDEX' :index+1,
        'BULAN_TAHUN':bulan_tahun,
        'TANGGAL' : tanggal,
        'KETERANGAN' : keterangan,
        'STATUS' : status,
        'AMMOUNT' : ammount
      })

    df = pd.DataFrame.from_dict(dtlist)
    df = df.sort_values(by=['INDEX'],ascending=False)

    last_saldo = re.findall("CLOSING\s+BALANCE\s+-(\d{1,3}([\.,]*\d{3})*([\.,]\d\d))",sufix)[0][0]
    print(last_saldo)
    last_saldo = last_saldo.replace(',','').replace('.','').strip()
    last_saldo = float(last_saldo)/100

    ammount = df['AMMOUNT'].values.tolist()
    saldo   = [last_saldo]


    for i in range(len(df)-1,0,-1):
      if df.iloc[[i]]['STATUS'].values[0] == 'DEBIT':
        saldo.append(saldo[-1]+ammount[i])
      else:
        saldo.append(saldo[-1]-ammount[i])

    df['SALDO'] = np.array(saldo)
    df = df.sort_values(by=['INDEX'])

    return df