import re
from datetime import datetime
import pandas as pd

class Danamon:
  def __init__(self):
    self.monthData = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.Danamon_table_spliting(df)

  def Danamon_table_spliting(self,df):
    tahun = re.findall('[A-Z]{3}\s+\d\d,(\d\d\d\d)',df[0])[0]

    df = df[1]
    dtlist = []

    lastSaldo = 0
    for index,er in enumerate(df):
      tanggal    = None
      keterangan = None
      ammount    = None
      saldo      = None
      status     = None

      tanggal     = re.findall('\d\d\/\d\d',er[0])[0]
      keterangan  = er[0].replace(tanggal,'').strip()

      tanggal     = tanggal.replace('/','')

      uang_kas    = er[1].replace(",","").replace(".","").strip().split(' ')
      try:
        uang_kas.remove('')
      except:
        pass

      if "_CREDIT" in uang_kas[0]:
        status       = 'CREDIT'
        uang_kas[0]  = uang_kas[0].replace('_CREDIT','')
      else:
        status = 'DEBIT'

      ammount = float(uang_kas[0])/100
      saldo   = float(uang_kas[1].replace('_CREDIT',''))/100

      bulan_tahun   = f"{self.monthData[int(tanggal[2:])-1]} {tahun}"
      tanggal       = f"{tahun}-{tanggal[2:]}-{tanggal[:2]}"

      dtlist.append({
        'INDEX' :index,
        'BULAN_TAHUN':bulan_tahun,
        'TANGGAL' : tanggal,
        'KETERANGAN' : keterangan,
        'STATUS' : status,
        'AMMOUNT' : ammount,
        'SALDO' : saldo,
      })

    df = pd.DataFrame.from_dict(dtlist)
    return df