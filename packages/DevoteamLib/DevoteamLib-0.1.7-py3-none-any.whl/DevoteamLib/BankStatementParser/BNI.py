import re
from datetime import datetime
import pandas as pd

class BNI:
  def __init__(self):
    self.monthData = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.BNI_table_spliting(df)

  def BNI_table_spliting(self,df):
    df = df[1]
    saldo_awal = ""
    pattern_ammount_saldo = '(\d{1,3}([\.,]\d{3})+(\.\d\d)*)'
    pattern_keterangan = "(?<=,\\d{4}).*|(?<=\d{2}).*|(?<=\d{1}).*|(?<=\d{3}).*"
    pattern_tanggal = '\d{2}/\d{2}/\d{4} '
    dictList = []

    for index,er in enumerate(df):
        tanggal     = ""
        bulan_tahun = ""
        keterangan  = ""
        status      = ""
        ammount     = ""
        saldo       = ""

        # get datetime
        try:
            if isinstance(er, str):
               er          = er.split("\n")
            date           = re.findall(pattern_tanggal, er[0])[0].strip()
            parsed_tanggal = datetime.strptime(date, '%d/%m/%Y')
            bulan          = self.monthData[parsed_tanggal.month - 1]

            data           = er
            bulan_tahun    = f'{bulan} {parsed_tanggal.year}'
            tanggal        = parsed_tanggal.strftime('%Y-%m-%d')
            str_ammount    = ""
            str_saldo      = ""

            # ambil ammount dan saldo
            regex_ammount_saldo = [data[1].split(" ")[0],data[1].split(" ")[2]]

            # kalau ada data ammount dan saldo
            if len(regex_ammount_saldo) == 2:
                str_ammount = regex_ammount_saldo[0]
                str_saldo = regex_ammount_saldo[1]

                ammount = float(str_ammount.replace(',', '').replace('.', ''))/100
                saldo = float(str_saldo.replace(',', '').replace('.', ''))/100

                keterangan = data[0]
                # setting status dan ammount
                if 'D' in data[1]:
                    status = "DEBIT"
                else:
                    # Kalau negatif berarti credit
                    status = "CREDIT"

            # hilangkan timestamp tanggal
            find_tanggal = re.findall('\d{2}\.\d{2}.\d{2}', keterangan)
            if len(find_tanggal) != 0:
               keterangan = keterangan.replace(find_tanggal[0], '')

            # hilangkan nomor depan
            find_nomor =  re.findall('\d* ', keterangan)
            keterangan = keterangan.replace(find_nomor[0], '')

            # hilangkan kode ref
            keterangan = re.findall('(?<=\d{6}).*', keterangan)[0]

            # ambil semua keterangan
            keterangan = keterangan.replace(date, '').replace(str_saldo, '').replace(str_ammount, '').strip()

            dictList.append({
               'INDEX' :index,
               'BULAN_TAHUN':bulan_tahun,
               'TANGGAL' : tanggal,
               'KETERANGAN' : keterangan.strip(),
               'STATUS' : status,
               'AMMOUNT' : ammount,
               'SALDO' : saldo,
            })

        except Exception as ex:
          print(ex)
          print(er)

    df = pd.DataFrame(dictList)
    df['AMMOUNT'] = df['AMMOUNT'].astype(float)

    return df