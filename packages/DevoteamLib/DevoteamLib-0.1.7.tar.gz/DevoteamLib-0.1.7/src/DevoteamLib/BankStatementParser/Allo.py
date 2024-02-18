import re
from datetime import datetime
import pandas as pd

class Allo:
  def __init__(self):
    self.monthData  = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]
    self.monthShort = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

  def extract(self,df):
    return self.Allo_table_spliting(df)

  def Allo_table_spliting(self,df):
    df            = df[1]
    dtlist        = []

    for index,er in enumerate(df):
      tanggal       = None
      keterangan    = None
      ammount       = None
      status        = None
      saldo         = None

      tanggal       = re.findall('(\d{1,2}\s+-\s+[A-Z]{3}\s+-\s+\d\d)',er[0])[0]
      keterangan    = er[0].replace(tanggal,'').strip()

      tanggal       = [x.strip() for x in tanggal.split('-')]
      bulan_tahun   = f"{self.monthData[int(self.monthShort.index(tanggal[1]))]} 20{tanggal[2]}"

      bulan         = int(self.monthShort.index(tanggal[1]))+1
      if bulan<10:
        bulan = f"0{bulan}"
      else:
        bulan = str(bulan)

      if int(tanggal[0])<10:
        tanggal[0] = f"0{tanggal[0]}"
      else:
        tanggal[0] = str(tanggal[0])

      tanggal       = f"20{tanggal[2]}-{bulan}-{tanggal[0]}"

      uang_kas      = [x.replace(",","").replace(".","").strip() for x in er[1].split(' ')]
      try:
        uang_kas.remove('')
      except:
        pass
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