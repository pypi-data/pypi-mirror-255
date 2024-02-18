import re
import os
import uuid
import json

import numpy as np

from google.cloud import storage
from langchain.llms import VertexAI

import shutil
from pdf2image import convert_from_path

import DevoteamLib
import DevoteamLib.OCRLayouting as OCRLayouting

def Merge(dict1, dict2):
  res = {**dict1, **dict2}
  return res

def getPrecision(gai_result,text_target):
  numFound      = 0

  for gr in gai_result:
    if gr in text_target:
      numFound+=1

  return numFound/len(gai_result)

def checkConfidence(json_result,text_conf):
  df_text_conf = {} 

  text_conf = text_conf.split(" ")
  text_conf = list(filter(None, text_conf))
  
  for tc in text_conf:
    df_text_conf['_'.join(tc.split('_')[:-1])] = float(tc.split('_')[-1])

  for jr in json_result[0].keys():
    try:
      if json_result[0][jr] is not None:
        text            = json_result[0][jr].split(' ')
        ocr_confidence   = []
        for t in text:
          try:
            ocr_confidence.append(df_text_conf[t])
          except:
            for dtc in df_text_conf.keys():
              if t in dtc:
                ocr_confidence.append(df_text_conf[dtc])
                break
        
        ocr_confidence   = np.mean(ocr_confidence)
        genai_confidence = getPrecision(text," ".join(text_conf))

        json_result[1][jr] = {
            'text'            : json_result[1][jr],
            'ocr_confidence'   : ocr_confidence,
            'genai_confidence' : genai_confidence
        }

      else:
        json_result[1][jr] = {
            'text'            : "Not Found",
            'ocr_confidence'   : 0,
            'genai_confidence' : 0
        }
    except:
      return f"Incorrect Spelling Detected '{jr}'"

  return json_result[1]

class GenAIDocExtract:
  def __init__(self, project_id:str):
    self.storage_client = storage.Client(project = project_id)

  def download_blob(self, bucket_name: str, source_blob_name: str, destination_file_name:str):
    bucket     = self.storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    return destination_file_name

  def textBisonNER(self, model_name = "text-bison@002",
                    max_output_tokens: int = 2048, temperature: int = 0,
                    top_p: int = 0.8, top_k: int = 40, verbose: bool = False,
                    prefix = "Bedasar pada Contex, Cari beberapa informasi berikut dalam bentuk json, kosongkan informasi bila tidak ditemukan. Buat 2 versi, versi 1 merupakan versi original dan versi 2 dimana terdapat perbaikan ejaan",
                    regexDict = {},
                    file_gcs_uri: str = '',
                    prompt: str = '',
                    ocr_layouting: bool = True) -> dict:
    if DevoteamLib.GenAIStatus('textBisonNER'):
      llm = VertexAI(
            model_name        = model_name,
            max_output_tokens = max_output_tokens,
            temperature       = temperature,
            top_p             = top_p,
            top_k             = top_k,
            verbose           = verbose
        )

      bucket,filename         = re.findall('gs:\/\/(.*?)\/(.*)',file_gcs_uri)[0]

      new_file_name           = f"{str(uuid.uuid4())}.{filename.split('.')[-1]}"

      self.download_blob(bucket, filename, new_file_name)

      context     = []
      context_con = []

      if filename.split('.')[-1].lower() not in ['jpg','jpeg','png','pdf']:
        return "Format file not supported"

      elif filename.split('.')[-1].lower() in ['jpg','jpeg','png']:
        resultOcr     = None
        if ocr_layouting:
          resultOcr = OCRLayouting.layout_normalization(new_file_name)
        else:
          resultOcr = OCRLayouting.horizontal_read(new_file_name, processOutput="row")

        prompt                  = f"Context: {''.join(resultOcr[0])} \n {prefix}\n{prompt}"
        context.append(' '.join(resultOcr[0]))
        context_con.append(' '.join(resultOcr[1]))
        os.remove(new_file_name)

      elif filename.split('.')[-1].lower() in ['pdf']:
        images = convert_from_path(new_file_name)
        if len(images)>5:
          os.remove(new_file_name)
          return "PDF file have more than 5 pages"

        foldername = str(uuid.uuid4())
        os.mkdir(foldername)

        for index,img in enumerate(images):
          img.save(f'{foldername}/image_save.png','PNG')
          resultOcr     = None
          if ocr_layouting:
            resultOcr = OCRLayouting.layout_normalization(f'{foldername}/image_save.png')
          else:
            resultOcr = OCRLayouting.horizontal_read(f'{foldername}/image_save.png', processOutput="row")

          context.append(' '.join(resultOcr[0]))
          context_con.append(' '.join(resultOcr[1]))

        prompt     = f"Context: {' '.join(context)} \n {prefix}\n{prompt}"
        shutil.rmtree(foldername)
        os.remove(new_file_name)

      print("Question :",prompt)
      answer       = [json.loads(aw) for aw in re.findall('(\{.*?\})',llm(prompt).replace('\n',' '))]
      source       = ' '.join(context)
      print("Answer   :",answer)

      for rd in regexDict.keys():
        regexDict[rd] = re.findall(regexDict[rd],source)[0]

      answer = [Merge(a,regexDict) for a in answer]

      answer = checkConfidence(answer,' '.join(context_con))
      if "Incorrect Spelling Detected" in answer:
        return answer

      new_answer = {}
      for key,val in (answer.items()):
        new_answer[key.replace(" ","_").lower()] = val

      total_confidence = []
      single_text      = []
      for cc in (' '.join(context_con)).split(' '):
        cc_data = cc.split("_")
        if len(cc) > 1:
          total_confidence.append(float(cc_data[1]))

          single_text.append({"text":cc_data[0],"ocrconfidence":float(cc_data[1])})

      new_answer['ocr_text_result'] = {
          'full_text': ' '.join(context),
          'ocrconfidence': np.mean(total_confidence),
          'single_text':single_text
      }

      return new_answer

    else:
      return "You not allowed to used this function"