import cv2
from PIL import Image
import numpy as np
import uuid
import shutil
import os
import base64
import random
import argparse
import re
import datefinder
import datetime
from paddleocr import PaddleOCR
import requests
import json
import base64
import aiohttp
import asyncio
import time
import pandas as pd
from app import mapping


async def call_api(url,data_json):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        async with session.post(url,json=data_json) as resp:
            response = await resp.json()
            return response
def dateaddress_detect(s):
   try:
        url = "https://api.ai21.com/studio/v1/j2-ultra/chat"
        payload = {
            "numResults": 1,
            "temperature": 0.7,
            "messages": [
                {
                    "text": f"{s}",
                    "role": "user"
                }
            ],
            "system": "You are POS receipt data expert, parse, detect, recognize and convert following receipt OCR image result into structure receipt data object."

        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "Bearer y4O1zZOvUh8W1FwGMruF1yme7V8xmC9G"
        }

        
        e = {
        "date": None,
        "address": None,
        "merchant_name":None
        
      }
        try:
         response = requests.post(url, json=payload, headers=headers)
         m = response.json()
         x = m["outputs"][0]["text"]
         data_dict = json.loads(x)
         e["date"] = data_dict["date"]
         e["address"] = data_dict["address"]
         e["merchant_name"] = data_dict["merchant_name"]
        except:
         response = requests.post(url, json=payload, headers=headers)
         m = response.json()
         x = m["outputs"][0]["text"]
         data_dict = json.loads(x)
         e["date"] = data_dict["date"]
         e["address"] = data_dict["address"]
         e["merchant_name"] = data_dict["merchant_name"]

 
   except Exception as er :
    print(f"Error : {er}")
   return e


def rtext(results):
 try: 
  t = 0
  e = 0
  r = 0
  w = 0
  strings = [[]]
  for sublist in results:
      for text in sublist:
        data = np.array(text[0])
        second_elements = data[:, 1]
        te = max(second_elements)
        if (te - t) >= 14  :
            e += 1
            strings.append([])
            strings[e].append(text[1][0])
        else:
          strings[e].append(text[1][0])
        t = text[0][3][1]
        r += text[0][3][1]
        w += 1


  s = ""
  d = dict()
  c = 0
  for i in strings :
    if len(i) > 0:
     s = s + ' '.join(i) + "\n"   
     d[f"line_{c}"] = ' '.join(i)
     c += 1
  q = str(s)
  j = """  {
        "date": ?,
        "address": ?,
        "merchant_name : ?
        }
"""     
  prompt=f"""### Instruction:
  You are POS receipt data expert, parse, detect, recognize and convert following receipt OCR image result into structure receipt data object.
  Don't make up value not in the Input. Output only date and address and merchant name IF NOT EXISTS return null must be a well-formed JSON object.```json
  ### Input:

  {q}

  ### Output:
  {j}   
  """
 except Exception as er :
  print(f"Error : {er}")   
 return (prompt,d,q)


def date(results):
 try: 
  now = datetime.datetime.now()
  m= datetime.datetime(2023, 1, 12, 00, 00)
  b = []
  x = []
  z = 2023
  s = 23
  y = '2Q23'
  w = 2024
  q = 24
  t = None
  paw = f"""\w+\/{y}.*|\w+\-{y}.*|\w+\.{y}.*|\d+AM$|\d+PM$|
          |\w+\/{s}.*|\w+\-{s}.*|\w+\.{s}.*|\w+\/{z}.*|\w+\-{z}.*|{z}.*|\w+\.{z}.*|
          \w+\/{w}.*|\w+\-{w}.*|\w+\.{w}.*|\w+\/{q}.*|\w+\-{q}.*|\w+\.{q}.*"""
  for sublist in results:
      for text in sublist:
        matchs = re.search(paw,text[1][0],flags=re.IGNORECASE)
        if matchs :
          x.append(text[1][0])

  if len(x) > 0:
      for j in x:
        matches = datefinder.find_dates(j)
        for i in matches:
          if i < now and i > m:
            b.append(i)
  if len(x) == 0:
   for sublist in results:
      for text in sublist:
        matches = datefinder.find_dates(text[1][0])
        for i in matches:
          if i < now and i > m:
            b.append(i)

  if len(b) <= 0 :
    t = x
  if len(x) <= 0 :
    r = list(set(b))
    t = r[0]
  else :
    t = x[0]
 except Exception as er :
  print(f"Error : {er}")   
 return t

def address(results):
 try : 
  a = ('ThuThiem','quan1', 'quan2', 'quan3', 'quan4', 'quan5', 'quan6', 'quan7', 'quan8', 'quan9', 'quan10',
      'quan11', 'quanthuduc', 'quanphunhuan', 'quangovap','quantan', 'quantanbinh', 'quanbinhthanh', 'HCMC',
      'TPHCM', 'HCM', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'HoChiMinh', 'Q8', 'Q9', 'Q10',
      'Q11', 'Q12', 'thuduc', 'phunhuan', 'govap', 'tanbinh', 'binhthanh', 'binhtan', 'HoChiMinh',
      'Q.1', 'Q.2', 'Q.3', 'Q.4', 'Q.5', 'Q.6', 'Q.7'
      , 'Q.8', 'Q.9', 'Q.10','Q.11', 'Q.12')

  b = []
  w = []
  p = []
  t = 0
  c = None
  for sublist in results:
      for text in sublist:
        for i in a:
          cleaned_text = re.sub(r"\s+|\.", "", text[1][0])
          matchs = re.search(i,cleaned_text,flags=re.IGNORECASE)
          if matchs:
              b.append(text[1][0])
          matchss = re.search(r"\bP\.\w+",text[1][0],flags=re.IGNORECASE)
          if matchss :
              w.append(text[1][0])
              if  len(sublist[t-1][1][0]) > 5 :
                w.append(sublist[t-1][1][0])
          matchsss = re.search(r"phuong\.(.*)",text[1][0],flags=re.IGNORECASE)
          if matchsss :
              w.append(text[1][0])

          # matchs = re.search(r' thanh .*|',i,flags=re.IGNORECASE)
          # if matchs :
          #   break

        t += 1
        r = tuple(set(b+w))
        c = str(r)

 except Exception as er :
  print(f"Error : {er}")       
 return c


def auto_rotate_resize_image(image_path) :
 try: 
  # Read the image
  image = cv2.imread(image_path)

  # Convert the image to grayscale
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

  # Detect the orientation
  orientation = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))

  # Calculate the angle of rotation
  angle = 0
  if cv2.countNonZero(orientation[:, :100]) > cv2.countNonZero(orientation[:, 100:]):
    angle = 90

  # Rotate the image if necessary
  if angle > 0:
    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
  # original_image = Image.open(original_image_path)
  original_image = Image.fromarray(image)
  # Get the original image dimensions
  original_width, original_height = original_image.size

  # Calculate the new height and width to maintain aspect ratio
  new_height = 720
  new_width = int((new_height / original_height) * original_width)

  # Resize the image
  resized_image = original_image.resize((new_width, new_height), Image.ANTIALIAS)

  resized_numpy_array = np.asarray(resized_image)
 except Exception as er :
  print(f"Error : {er}")    
 return  resized_numpy_array


def sorted_boxes(dt_boxes):
    """
    Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes with shape [4, 2]
    return:
        sorted boxes(array) with shape [4, 2]
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[0][1], x[0][0]))
    _boxes = list(sorted_boxes)
    threshold_value_y = 10
    for j in range(5):
      for i in range(num_boxes - 1):
          if abs(_boxes[i + 1][0][1] - _boxes[i][0][1]) < threshold_value_y and (_boxes[i + 1][0][0] < _boxes[i][0][0]):
              tmp = _boxes[i]
              _boxes[i] = _boxes[i + 1]
              _boxes[i + 1] = tmp
    return _boxes


def relocate(results : list) -> list:
 try:
  re = np.array(results)
  result = sorted_boxes(re) 
  t = 0
  e = 0
  r = 0
  w = 0
  strings = [[]]
  for sublist in result:
      for text in sublist:
        data = np.array(text[0])
        second_elements = data[:, 1]
        te = float((float(sum(second_elements))/4))
        if (te - t) >= 4  :
            e += 1
            strings.append([])
            strings[e].append(text[1][0])
        else:
          strings[e].append(text[1][0])
        t = text[0][3][1]
        r += text[0][3][1]
        w += 1
 except Exception as er :
   print(f"Error : {er}")   
 return strings   

def extract_item(strings : list) -> list:
 try:
  x = []
  y = []
  e = r'\d+\.\d{3}\b|\d+\,\d{3}\b|\d+\ \d{3}\b|\d+\.*?000$|\d+\.*?000d$|\d+\.*?00d$|\d+\*?000$|\d+\,*?00d$'
  df = pd.read_csv('/work/key/key.csv')
  pa = ""
  for j in list(df["filter_item"]):
      pa += f"""{j}(.*)|"""
  new_string = pa[:(len(pa) - 1)] + pa[(len(pa) - 1) + 1:]
  par = str(new_string)
  for i in strings :

    for j in i:
      regex = re.compile(par,flags=re.IGNORECASE)
      mathss12 = regex.search(j)
      if mathss12 :
        try:
         del x[x.index(i)]
        except:
         pass
        break
      matchs = re.search(e, j,flags=re.IGNORECASE)
      textx = " ".join([str(item) for item in i])
      if matchs :
        textx.replace(matchs.group(), "")
        regex = re.compile(par,flags=re.IGNORECASE)
        mathss12 = regex.search(textx)
        if mathss12 :
          try:
           del x[x.index(i)]
          except:
           pass
          break
        alphabetic_pattern = re.compile("[a-zA-Z]")
        has_alphabet = bool(alphabetic_pattern.search(j))
        if len(i) == 1 and has_alphabet == False:
          break
        elif len(i) == 1 and has_alphabet == True:
          x.append([i[0].replace(f"{matchs.group()}",""),matchs.group()])
          break
        if i not in x  :
          x.append(i)
          m = (strings.index(i))
          g = x.index(i)
          if len(strings[m-1]) <= 1 :
              textt = strings[m-1][0]
          else :
              textt = " ".join([str(item) for item in strings[m-1]])
          matchs1 = re.search(e,textt,flags=re.IGNORECASE)
          matchsq = re.search(par,textt,flags=re.IGNORECASE)
          if (not matchs1) and (not matchsq) and (strings[m-1]not in y):
            y.append(strings[m-1])

        else:
          if len(strings[m-2]) <= 1 :
              textt = strings[m-2][0]
          else :
              textt = " ".join([str(item) for item in strings[m-1]])
          matchs11 = re.search(e,textt,flags=re.IGNORECASE)
          matchsq1 = re.search(par,textt,flags=re.IGNORECASE)
          if (not matchs11) and (not matchsq1) and (strings[m-1]not in y):
            y.append(strings[m-2])

          else:
            if len(strings[m+1]) <= 1 :
              text = strings[m+1][0]
            else :
              text = " ".join([str(item) for item in strings[m+1]])
            matchs2 = re.search(e,text,flags=re.IGNORECASE)
            matchsp = re.search(par,text,flags=re.IGNORECASE)
            if not matchs2 and (strings[m+1]not in y) :
              if matchsp :
                break
              else:
                y.append(strings[m+1])




  if len(y) > 0 :
      for i in range (len(y)):
       if i > 1 :
        if len(y[i]) > 0 and y[i] not in x[i-1] :
          x[i].append(y[i][0])
       else:
        if len(y[i]) > 0  :
          x[i].append(y[i][0])
        else:
          x[i].append(y[None])
 except Exception as er :
  print(f"Error : {er}")
 return x

def item_api_ouput(x : list) -> list:
 try:
  w = 0
  c = {}
  e = r'\d+\.\d{3}\b|\d+\,\d{3}\b|\d+\ \d{3}\b|\d+\.*?000$|\d+\.*?000d$|\d+\.*?00d$|\d+\*?000$'
  for i in x:
    items = {"item":None,"price":[]}
    t = []
    for item in i:
        numbers = re.search(e, item)
        if numbers:
          cleaned_number = numbers[0].replace(",", "").replace(".", "").replace("d", "").replace(" ", "")
          items["price"].append(float(cleaned_number))
        else:
          t.append(str(item))
          items["item"] = ' '.join(t)
    items["price"] = max(items["price"])
    c[f"item_{w}"] = items
    w += 1
 except Exception as er :
  print(f"Error : {er}")
 return c


def header(results : list,map : list) -> list:
 try: 
  y = {}
  x = 1
  df = pd.read_csv('/work/key/key.csv')
  pa = ""
  for j in list(df["filter_header"]):
      pa += f"""{j}(.*)|"""
  new_string = pa[:(len(pa) - 1)] + pa[(len(pa) - 1) + 1:]
  p = str(new_string)
  for i in results :
      textx = " ".join([str(item) for item in i])
      matchs = re.search(p,textx,flags=re.IGNORECASE)
      if matchs :
         break
      else:
        if len(i) > 0 :
         if  i[0] not in map :
          s = ' '.join(i) 
          y[f"header_{x}"] = s
          x+=1
 except Exception as er :
  print(f"Error : {er}")     
 return y




def extra(results : list) -> list:
 try: 
  c = []
  pa = r'\d+\.\d{3}\b|\d+\,\d{3}\b|\d+\ \d{3}\b|\d+\.*?000$|\d+\.*?000d$|\d+\.*?00d$|\d+\*?000$'
  results.reverse()
  for i in results :
      textx = " ".join([str(item) for item in i])
      matchs = re.search(pa,textx,flags=re.IGNORECASE)
      if matchs :
         break
      else:
        if len(i) > 0 :
         s = ' '.join(i) 
         c.append(s)
  c.reverse()
 except Exception as er :
  print(f"Error : {er}")   
 return c

def total(strings,item):
 try:
  x = []
  y = None
  e = r'''\d+\.\d{3}\b|\d+\,\d{3}\b|\d+\ \d{3}\b|\d+\.*?000$|\d+\.*?000d$|\d+\*?000$|\d+\,*?000d$|\d+\.*?00d$|\d+\,*?00d$'''
  df = pd.read_csv('/work/key/key.csv')
  pa = ""
  for j in list(df["filter_total"]):
      pa += f"""{j}(.*)|"""
  new_string = pa[:(len(pa) - 1)] + pa[(len(pa) - 1) + 1:]
  p = str(new_string)
  for i in strings :
   for j in i:
    textx = " ".join([str(item) for item in i])
    regex = re.compile(p,flags=re.IGNORECASE)
    mathss1 = regex.search(textx)
    if mathss1 :
        try:
         del x[x.index(i)]
        except:
         pass
        break
    else:
      regex = re.compile(e,flags=re.IGNORECASE)
      mathss12 = regex.search(j)
      if mathss12 :
          alphabetic_pattern = re.compile("[a-zA-Z]")
          # Check if the string contains any alphabetic characters
          has_alphabet = bool(alphabetic_pattern.search(j))
          if has_alphabet == False:
            cleaned_number = j.replace(",", "").replace(".", "").replace("d", "").replace(" ", "")
            x.append(float(cleaned_number))  
          elif has_alphabet == True:
            c = re.sub(r'[a-zA-Z]', '', j)
            cleaned_number = j.replace(",", "").replace(".", "").replace("d", "").replace(" ", "")
            try:
             x.append(float(cleaned_number))
            except:
             cleaned_number = mathss12.group().replace(",", "").replace(".", "").replace("d", "").replace(" ", "") 
             x.append(float(cleaned_number))
  t = 0
  for _,j in item.items():
   t += j['price']
  h = 10**len(str(int(t)))
  m = [e  for e in x if e < h]
  if len(m) == 0:
    y = t
  else:
    y = max(m)
 except Exception as er :
  print(f"Error : {er}")
 return y




def endpoint(img:str) -> str:
 try: 
  # base64_image_string = "your_base64_encoded_image_string"
  a = img.replace("data:image/jpeg;base64,", "").replace("data:image/jpg;base64,", "").replace("data:image/png;base64,", "")
  decoded_bytes = base64.b64decode(a)
  t = uuid.uuid4()

  with open(f"{t}.jpg","wb") as f:  # Adjust filename and extension as needed
      f.write(decoded_bytes)

  img = auto_rotate_resize_image(f"{t}.jpg")
  ocr = PaddleOCR(lang="en",ocr_version="PP-OCRv4",use_gpu = False,cls = True,det_lang='ml') # Specify language (optional)
  results = ocr.ocr(img)
  # delete_img(t)
  if len(rtext(results)[2]) < 100 :
    bill_checking = False
  else:
    bill_checking = True
 
  amap = mapping.header_map(mapping.nrelocate(results))[0]
  ta = dateaddress_detect(rtext(results)[0])
  amap.update(ta)
  check =  mapping.header_map(mapping.nrelocate(results))[1]

  response = {
          "header":header(relocate(results),check),
          "header_mapping":amap,
          "data_items":item_api_ouput(extract_item(relocate(results))),
          "Total":total(relocate(results),item_api_ouput(extract_item(relocate(results)))),
          "extra":extra(relocate(results)),
          "bill_checking":bill_checking,
          "raw":rtext(results)[1]
          }
   
 except Exception as e :
  print(f"Error : {e}") 

 return response
  
def delete_img(t : str): 
  i = f"{t}.jpg"  
  try:
          os.remove(i)  # Remove individual files
  except FileNotFoundError:
          print(f"File not found: {i}")  # Handle errors gracefully
  except PermissionError:
          print(f"Insufficient permissions to remove: {i}")

if __name__ == "__main__":
  pass
