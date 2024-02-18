import re
from datetime import datetime
import pandas as pd

class HANA:
  def __init__(self):
    self.monthData = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.HANA_table_spliting(df)

  def HANA_table_spliting(self,df):
    sufix         = df[2]
    df            = df[1]
    dtlist        = []

    for index,er in enumerate(df):
      tanggal       = None
      keterangan    = None
      ammount       = None
      status        = None
      saldo         = None

      tanggal       = re.findall('(\d\d\/\d\d\/\d{4})',er[0])[0]
      keterangan    = er[0].replace(tanggal,'').strip()

      tanggal       = tanggal.split('/')
      bulan_tahun   = f"{self.monthData[int(tanggal[0])-1]} {tanggal[2]}"

      tanggal       = f"{tanggal[2]}-{tanggal[0]}-{tanggal[1]}"

      uang_kas      = []
      for x in er[1].replace('USD','').split(' '):
        if re.search("[0-9]+", x):
          uang_kas.append(x.strip())

      ammount       = uang_kas[0]
      saldo         = uang_kas[1].replace('_CREDIT','')

      if "_CREDIT" in ammount:
        status    = 'CREDIT'
        ammount   = ammount.replace('_CREDIT','')
      else:
        status = 'DEBIT'

      if '.' in ammount or ',' in ammount:
        ammount = ammount.replace(',','').replace('.','')
        ammount = float(ammount)/100
      else:
        ammount = float(ammount)

      if '.' in saldo or ',' in saldo:
        saldo = saldo.replace(',','').replace('.','')
        saldo = float(saldo)/100
      else:
        saldo = float(saldo)

      dtlist.append({
        'INDEX' :index+1,
        'BULAN_TAHUN':bulan_tahun,
        'TANGGAL' : tanggal,
        'KETERANGAN' : keterangan,
        'STATUS' : status,
        'AMMOUNT' : ammount,
        'SALDO'   : saldo
      })

    df = pd.DataFrame.from_dict(dtlist)

    return df