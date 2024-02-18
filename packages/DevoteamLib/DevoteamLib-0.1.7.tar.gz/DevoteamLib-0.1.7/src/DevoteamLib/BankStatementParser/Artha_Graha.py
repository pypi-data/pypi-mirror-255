import re
from datetime import datetime
import pandas as pd

class Artha_Graha:
  def __init__(self):
    self.monthData  = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.Artha_Graha_table_spliting(df)

  def Artha_Graha_table_spliting(self,df):
    df            = df[1]
    dtlist        = []

    for index,er in enumerate(df):
      tanggal       = None
      keterangan    = None
      ammount       = None
      status        = None
      saldo         = None

      tanggal       = re.findall('(\d{2}\/\d{2}\/\d{4})',er[0])[0]
      print(er[0],tanggal)
      keterangan    = er[0].replace(tanggal,'').strip()
      tanggal       = tanggal.split("/")


      bulan_tahun   = f"{self.monthData[int(tanggal[1])-1]} {tanggal[2]}"

      tanggal       = f"{tanggal[2]}-{tanggal[1]}-{tanggal[0]}"

      uang_kas      = []
      for x in er[1].split(' '):
        if re.search("[0-9]+", x):
          uang_kas.append(x.replace(",","").replace(".","").strip())

      print(uang_kas)
      ammount       = uang_kas[0]
      saldo         = uang_kas[1].replace('_CREDIT','')

      if "_CREDIT" in ammount:
        status    = 'CREDIT'
        ammount   = ammount.replace('_CREDIT','')
      else:
        status    = 'DEBIT'

      ammount     = float(ammount)/100
      saldo       = float(saldo)/100

      dtlist.append({
        'INDEX' :index+1,
        'BULAN_TAHUN':bulan_tahun,
        'TANGGAL' : tanggal,
        'KETERANGAN' : keterangan,
        'STATUS' : status,
        'AMMOUNT' : ammount,
        'SALDO' : saldo
      })

    df = pd.DataFrame.from_dict(dtlist)

    return df