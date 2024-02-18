import re
from datetime import datetime
import pandas as pd

class MEGA:
  def __init__(self):
    self.monthData  = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.MEGA_table_spliting(df)

  def MEGA_table_spliting(self,df):
    df            = df[1]
    dtlist        = []

    for index,er in enumerate(df):
      tanggal       = None
      keterangan    = None
      ammount       = None
      status        = None
      saldo         = None

      tanggal       = re.findall('(\d{1,2}\/\d{1,2}\/\d{2})',er[0])[0]
      keterangan    = er[0].replace(tanggal,'').strip()
      tanggal       = tanggal.split("/")
      print(tanggal)

      bulan_tahun   = f"{self.monthData[int(tanggal[0])-1]} 20{tanggal[2]}"

      bulan         = int(tanggal[0])
      if bulan<10:
        bulan = f"0{bulan}"
      else:
        bulan = str(bulan)

      if int(tanggal[1])<10:
        tanggal[1] = f"0{tanggal[1]}"
      else:
        tanggal[1] = str(tanggal[1])

      tanggal       = f"20{tanggal[2]}-{bulan}-{tanggal[1]}"
      print(tanggal)

      uang_kas      = [x.replace(",","").replace(".","").strip() for x in er[1].split(' ')]
      try:
        uang_kas.remove('')
      except:
        pass
      print(uang_kas)


      ammount       = float(uang_kas[0])/100
      saldo         = float(uang_kas[-1])/100

      if ammount == 0:
        status    = 'CREDIT'
        ammount   = float(uang_kas[1])/100
      else:
        status    = 'DEBIT'

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