import DevoteamLib

import os
import re
import PIL
import time
import json
import pickle
import numpy as np
import pandas as pd

import cv2
from scipy.ndimage import interpolation as inter
from scipy.ndimage import rotate

import google.auth
import google.auth.transport.requests

from google.cloud import vision

## Image Skewing
def correct_skew(image, delta=1, limit=5):
  if DevoteamLib.OCRLayoutingStatus('correct_skew'):
    def determine_score(arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1, dtype=float)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2, dtype=float)
        return histogram, score

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    scores = []
    angles = np.arange(-limit, limit + delta, delta)
    for angle in angles:
        histogram, score = determine_score(thresh, angle)
        scores.append(score)

    best_angle = angles[scores.index(max(scores))]

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, best_angle, 1.0)
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, \
            borderMode=cv2.BORDER_REPLICATE)

    return best_angle, corrected
  else:
    return "You not allowed to used this function"

## Similarity Between 2 Array
def jaccard_similarity(x,y):
  if DevoteamLib.OCRLayoutingStatus('jaccard_similarity'):
    """ returns the jaccard similarity between two lists """
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    return intersection_cardinality/float(union_cardinality)
  else:
    return "You not allowed to used this function"

## OCR Using Google Vision API
def detect_text(path):
  if DevoteamLib.OCRLayoutingStatus('detect_text'):
    """Detects text in the file."""

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    texts = response.text_annotations

    confidence = []
    for p in response.full_text_annotation.pages:
        for b in p.blocks:
            for par in b.paragraphs:
                for w in par.words:
                    confidence.append(w.confidence)

    df_text = {
      "text":[],
      "y_pos":[],
      "x_pos":[]
    }
    x_pos = 1
    for i in range(1,len(texts)):
      df_text['text'].append(texts[i].description+'_'+str("{:.5f}".format(confidence[i-1])))
      # df_text['text'].append(texts[i].description)
      df_text['y_pos'].append([texts[i].bounding_poly.vertices[x].y for x in range(4)])
      df_text['x_pos'].append([texts[i].bounding_poly.vertices[x].x for x in range(4)])
    df_text = pd.DataFrame.from_dict(df_text)

    return df_text

  else:
    return "You not allowed to used this function"

## Ordering OCR Result
def funcPosition(df,pos):
  if DevoteamLib.OCRLayoutingStatus('funcPosition'):
    start_i = 0
    end_i   = 1

    datacur = 0
    newdata = []

    for i in range(1,len(df)):
        data_before  = [x for x in range(min(df.iloc[[i-1]][pos].values[0]),max(df.iloc[[i-1]][pos].values[0])+1)]
        data_current = [x for x in range(min(df.iloc[[i]][pos].values[0]),max(df.iloc[[i]][pos].values[0])+1)]

        if jaccard_similarity(data_before,data_current)<0.35:
            newdata.append(df.iloc[start_i:end_i])
            start_i = end_i
            end_i   = i
        if end_i != start_i:
            try:
                newdata[-1] = df.iloc[start_i:end_i]
            except:
                newdata.append(df.iloc[start_i:end_i])

    try:
      newdata.append(df.iloc[end_i:])
      newdata[1] = pd.concat(newdata[:2])
    except:
      newdata.append(df.iloc[:end_i])
      newdata[1] = pd.concat(newdata[:2])
    return newdata[1:]
  else:
    return "You not allowed to used this function"

## Creating Black Box for Spliting Text in Image
def blockingImage(im_bw,size):
  if DevoteamLib.OCRLayoutingStatus('blockingImage'):
    length,width = im_bw.shape

    for w in range(0,width-size,size):
      for l in range(0,length-size,size):
        if 0 in im_bw[l:l+size,w:w+size]:
          im_bw[l:l+size,w:w+size] = 0

    return im_bw
  else:
    return "You not allowed to used this function"

## Split Black Box of Text Image Based on Y Line
def blockImage(im_bw):
  if DevoteamLib.OCRLayoutingStatus('blockImage'):
    margin = round(im_bw.shape[1]*0.01)
    length,width = im_bw.shape
    x_cut = []
    for ib in im_bw:
      listrow = ib.tolist()
      try:
        start_x = listrow.index(0)
        listrow.reverse()
        end_x   = listrow.index(0)

        x_cut.append([start_x,width-end_x])
      except:
        x_cut.append([])

    len_x         = [len(x) for x in x_cut]
    block_x       = []
    x_start_point = False
    for index in range(len(len_x)-1):
      if len_x[index+1] == 2 and not x_start_point:
        x_start_point = index+1
      elif len_x[index+1] == 0 and x_start_point:
        block_x.append([x_start_point,index+1])
        x_start_point = False

    fix_x = []
    for index,fx in enumerate(block_x):
      dx              = np.array(x_cut[fx[0]:fx[1]]).flatten().tolist()
      block_x[index]  = [fx[0]-round(margin/2),fx[1]+round(margin/2)]
      fix_x.append([min(dx)-margin,max(dx)+margin])

    return fix_x,block_x,margin
  else:
    return "You not allowed to used this function"

## Split Black Box of Text Image Based on X Line
def columns_Check(img,marginBlock,size):
  if DevoteamLib.OCRLayoutingStatus('columns_Check'):
    img_pos         = img.copy().T
    img_pos_backup  = img_pos.copy()

    blocking        = blockingImage(img_pos,size)
    lenght,width    = blocking.shape

    imgsave         = []
    imgsaveCorr     = []
    getStart        = False
    index_start     = 0
    for b in range(marginBlock,len(blocking)-marginBlock):
      # print(np.mean(blocking[b]))
      if np.mean(blocking[b]) > 230 and getStart:
        # print('Mulai')
        imgsave.append(img_pos_backup[index_start:b+round(marginBlock/2),:])
        imgsaveCorr.append([index_start,b+round(marginBlock/2)])
        getStart = False
      elif np.mean(blocking[b]) <= 230 and not getStart:
        getStart     = True
        index_start  = b
        # print('selesai')

    if getStart:
      imgsave.append(img_pos_backup[index_start:lenght,:])
      imgsaveCorr.append([index_start,lenght])
      getStart = False

    # for i in imgsave:
    #   imgplot         = plt.imshow(i.T)
    #   plt.show()

    return [x.T for x in imgsave],imgsaveCorr
  else:
    return "You not allowed to used this function"

## Main Of Layouting Function
def layout_normalization(file_name):
  if DevoteamLib.OCRLayoutingStatus('layout_normalization'):
    img             = PIL.Image.open(file_name)
    data_img        = np.asarray(img)

    _ , corrected   = correct_skew(data_img)

    gray_image      = cv2.cvtColor(corrected, cv2.COLOR_BGR2GRAY)

    (thresh, im_bw) = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    length,width    = im_bw.shape

    img_blank       = np.array([[255]*width]*length)

    data_y_and_x = detect_text(file_name)
    data_y_and_x.to_csv('data.csv')

    for x in data_y_and_x.values:
      img_blank[min(x[1]):max(x[1]),min(x[2]):max(x[2])] = im_bw[min(x[1]):max(x[1]),min(x[2]):max(x[2])]

    im_bw           = img_blank
    im_bw_backup    = im_bw.copy()

    size            = round(min([length,width])*0.01)

    blocking        = blockingImage(im_bw.copy(),size)

    fix_x,block_x,marginBlock = blockImage(blocking)

    img_data_ext = []

    data_y_and_x['y_pos_range'] = data_y_and_x['y_pos'].apply(lambda y:round(np.mean(y)))

    data_split_by_y      = []
    resultDataLayout     = []
    resultDataLayout_con = []
    for index,bx in enumerate(block_x):
      imgSplit, imgCorrSplit = columns_Check(im_bw_backup[block_x[index][0]:block_x[index][1],fix_x[index][0]:fix_x[index][1]],marginBlock,size)
      img_data_ext += imgSplit

      block_x_curr = data_y_and_x[(data_y_and_x['y_pos_range'] >= bx[0]) & (data_y_and_x['y_pos_range'] <= bx[1])].copy()
      block_x_curr['x_pos_range'] = block_x_curr['x_pos'].apply(lambda x:round(np.mean([min(x)-fix_x[index][0],max(x)-fix_x[index][0]])))

      for ics in imgCorrSplit:
        block_y_curr = block_x_curr[(block_x_curr['x_pos_range'] >= ics[0]) & (block_x_curr['x_pos_range'] <= ics[1])].copy()
        df_x_result = funcPosition(block_y_curr,'y_pos')

        fulltext_con = ''
        fulltext     = ''

        for df_x in df_x_result:
          df_x['x_pos'] = df_x['x_pos'].apply(lambda x:min(x))
          df_x          = df_x.sort_values(by=['x_pos']).reset_index(drop=True)
          fulltext     += ' '.join(['_'.join(cltext.split('_')[:-1]) for cltext in df_x.text.values.tolist()]).replace(' , ',',').replace(' . ','.').replace(' / ','/')+' '
          fulltext_con += ' '.join(df_x.text.values.tolist()).replace(' , ',',').replace(' . ','.').replace(' / ','/')+' '

        resultDataLayout.append(fulltext)
        resultDataLayout_con.append(fulltext_con)
        data_split_by_y.append(block_y_curr)

    return resultDataLayout,resultDataLayout_con
  else:
    return "You not allowed to used this function"
  
def horizontal_read(file_name,processOutput = "default"):
  if DevoteamLib.OCRLayoutingStatus('horizontal_read'):
    data_y_and_x = detect_text(file_name)
    data_y_and_x = data_y_and_x.sort_values(by=['y_pos']).reset_index(drop=True)

    df_x_result         = funcPosition(data_y_and_x,'y_pos')

    if processOutput == "default":
      for index,d in enumerate(df_x_result):
        d['x_pos']          = d['x_pos'].apply(lambda x:[x[0]])
        d['text']           = d['text'].apply(lambda x:x.split('_')[0])
        df_x_result[index]  = d
      return df_x_result

    elif processOutput == "row":

      resultDataLayout        = []
      resultDataLayout_con    = []

      for index,d in enumerate(df_x_result):
        d['x_pos']          = d['x_pos'].apply(lambda x:[x[0]])
        df_x_result[index]  = d

      for df_x in df_x_result:
        df_x = df_x.sort_values(by=['x_pos']).reset_index(drop=True)
        resultDataLayout_con.append(' '.join(df_x.text.values.tolist()))
        resultDataLayout.append(' '.join([d.split("_")[0] for d in df_x.text.values.tolist()]))

      return resultDataLayout,resultDataLayout_con
  else:
    return "You not allowed to used this function"