import re
from datetime import datetime
import pandas as pd

class Permata:
  def __init__(self):
    self.monthData = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.Permata_table_spliting(df)

  def Permata_table_spliting(self,df):
    tahun = re.findall('TANGGAL\s+CETAK\s+\:.*(\d{4})',df[0])[0]

    df = df[1]
    dtlist = []

    lastSaldo = 0
    for index,er in enumerate(df):
      tanggal    = None
      keterangan = None
      ammount    = None
      saldo      = None
      status     = None

      print(er)

      if index == 0:
        tanggal     = re.findall('\d{4}',df[1][0])[0]
        keterangan  = er[0]
        ammount     = 0
        saldo       = float(er[1].strip().replace(",","").replace(".",""))/100
        status      = "CREDIT"

      else:
        tanggal     = re.findall('\d{4}',er[0])[0]
        keterangan  = er[0].replace(tanggal,'').strip()

        uang_kas    = er[1].replace(",","").replace(".","").strip().split(" ")

        try:
          ammount     = float(uang_kas[0])/100
          saldo       = float(uang_kas[1])/100
        except:
          kas_after   = df[index+1][1].replace(",","").replace(".","").strip().split(" ")
          ammount_aft = float(kas_after[0])/100
          saldo_aft   = float(kas_after[1])/100

          kas         = float(uang_kas[0])/100

          if (kas + lastSaldo == saldo_aft + ammount_aft) or (kas - lastSaldo == saldo_aft - ammount_aft) or (kas - lastSaldo == saldo_aft + ammount_aft) or (kas + lastSaldo == saldo_aft - ammount_aft):
            ammount = kas
            saldo   = kas + lastSaldo

          else:
            ammount = ((kas-lastSaldo)**2)**0.5
            saldo   = kas

          if (saldo-ammount != saldo_aft) or (saldo-ammount != saldo_aft):
            temp    = ammount
            ammount = saldo
            saldo   = temp

        if lastSaldo-ammount == saldo:
          status    = "DEBIT"
        else:
          status    = "CREDIT"


      lastSaldo     = saldo
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