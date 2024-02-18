import re
from datetime import datetime
import pandas as pd

class OCBC:
  def __init__(self):
    self.monthData = ["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"]

  def extract(self,df):
    return self.OCBC_table_spliting(df)

  def OCBC_table_spliting(self,df):
    df = df[1]
    pattern_tanggal = '\d{1,2}\/\d{1,2}\/\d{2}'
    dictList = []

    for index, er in enumerate(df):
        tanggal = ""
        keterangan = ""
        status = ""
        ammount = ""
        saldo = ""
        bulan_tahun = ""

        # get datetime
        try:
            if isinstance(er, str):
               er = er.split("\n")
            date           = re.findall(pattern_tanggal, er[0])[0].strip()
            parsed_tanggal = datetime.strptime(date, '%d/%m/%y')
            bulan          = self.monthData[parsed_tanggal.month - 1]

            data = er
            bulan_tahun    = f'{bulan} {parsed_tanggal.year}'
            tanggal        = parsed_tanggal.strftime('%Y-%m-%d')
            str_debit      = ""
            str_kredit     = ""
            str_saldo      = ""
            keterangan     = data[0]

            # ambil ammount
            regex_ammount_saldo = data[1].strip().split(' ')
            try:
               regex_ammount_saldo.remove('')
            except:
               pass
            # print("Sebelum Regex     :",data[0])
            # print("Perhitungan Saldo :",regex_ammount_saldo)
            # print("=====================")

            # kalau ada data ammount dan saldo
            if len(regex_ammount_saldo) >= 3:
                str_debit   = regex_ammount_saldo[0]
                str_kredit  = regex_ammount_saldo[1]
                str_saldo   = regex_ammount_saldo[2]

                debit       = str_debit.replace(",", '').replace(".", '')
                kredit      = str_kredit.replace(",", '').replace(".", '')
                saldo       = str_saldo.replace(",", '').replace(".", '')

                debit       = [x for x in debit]
                kredit      = [x for x in kredit]
                saldo       = [x for x in saldo]

                debit.insert(-2, '.')
                kredit.insert(-2, '.')
                saldo.insert(-2, '.')

                debit       = float(''.join(debit))
                kredit      = float(''.join(kredit))
                saldo       = float(''.join(saldo))

                if int(debit) == 0:
                    status = "CREDIT"
                    ammount = kredit
                    keterangan = keterangan.replace(str_kredit, "")
                elif int(kredit) == 0:
                    status = "DEBIT"
                    ammount = debit
                    keterangan = keterangan.replace(str_debit, "")

            # ambil semua keterangan
            keterangan = keterangan.replace(date, "").replace(str_saldo, '').replace(str_debit, '').replace(str_kredit, '').strip()
            data[0] = ''

            # print(regex_ammount_saldo,ammount)

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