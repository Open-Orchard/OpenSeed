#!/usr/bin/python
import cgi
import cgitb
import sys
import mysql.connector
import hashlib
import json
import datetime
import random
sys.path.append("..")

import openseed_account as Account

import openseed_setup as Settings

settings = Settings.get_settings()

form = cgi.FieldStorage()


action = form.getvalue("act")
register = form.getvalue('register')
validusers = form.getvalue('validusers')
thetype = form.getvalue('type')

def to_char(thecode):
 code = ""
 num = 0
 while num < len(thecode):
   code = code+chr(int(thecode[num:num+2]))
   num = num + 2

 return code

def crypt_key():
 fullstring = ""
 while len(fullstring) < 256:
 	fullstring = fullstring+str(random.random()).split(".")[1]\
	      +to_char(str(random.random()).split(".")[1])\
              +str(random.random()).split(".")[1]\
              +to_char(str(random.random()).split(".")[1])


 count1 = 0
 count2 = 0
 mixer1 = ""
 mixer2 = ""
 mixer3 = ""
 for m1 in fullstring:
  if count1 % 2 == 0:
   mixer1 = mixer1+m1
  else:
   mixer2 = mixer2+m1.upper()
   count1 +=1
 hash1 = hashlib.md5(mixer1.encode())
 hash2 = hashlib.md5(mixer2.encode())
 mixer3 = str(mixer1.encode())+str(hash1.hexdigest())+str(mixer2.encode())+str(hash2.hexdigest()).replace(" ","2").replace("/","1").replace("'","0").replace(",","5").replace('"',"6").replace(':',"C").replace('#',"P").replace('\!',"p")
 mixer3 = mixer3.replace("`","A").replace("&","Q").replace("=","E").replace("(","T").replace(")","t")
 mixer3 = mixer3.replace("[","3").replace("]","9").replace("-","H").replace("+","h").replace("*","W").replace("%","w").replace("^","K")
 mixer3 = mixer3.replace("@","3").replace("$","9").replace("_","H").replace(";","h").replace("|","W").replace("{","w").replace("}","K")
 mixer3 = mixer3.replace("<","3").replace(">","9").replace("!","H").replace("~","h").replace('\?',"p").replace('\.',"p").replace('.',"p")
 mixer3 = mixer3.replace("\'","3").replace('\"',"9").replace("\,","H").replace("\~","h").replace('\:',"p").replace('\#',"p").replace('.',"p").replace("\\","F")
 
 return mixer3

def store_onetime(thetype,register,validusers):
 code = crypt_key()
 openseed = mysql.connector.connect(
		host = "localhost",
		user = "openseed",
		password = "b3V4ug3",
		database = "openseed"
		)
 mysearch = openseed.cursor()
 check = "SELECT codenum FROM onetime WHERE code = %s"
 val = (code,)
 mysearch.execute(check,val)
 result = mysearch.fetchall()
 if len(result) < 1:
  insert = "INSERT INTO `onetime` (type,code,registered,validusers) VALUES (%s,%s,%s,%s)"
  vals = (thetype,code,register,validusers)
  mysearch.execute(insert,vals)
  openseed.commit()

 mysearch.close()
 openseed.close()

 return code

def update_key(thetype,register,validusers):
 reg = ""
 code = ""
 openseed = mysql.connector.connect(
		host = "localhost",
		user = settings["dbuser"],
		password = settings["dbpassword"],
		database = "openseed"
		)
 mysearch = openseed.cursor()
 check = "SELECT registered,code FROM onetime WHERE validusers = %s AND type = %s"
 val1 = (validusers,thetype)
 val2 = (validusers.split(",")[1]+","+validusers.split(",")[0],thetype)
 mysearch.execute(check,val1)
 result1 = mysearch.fetchall()
 mysearch.execute(check,val2)
 result2 = mysearch.fetchall()

 if validusers.find(Account.user_from_id(register)) != -1: 
  if len(result1) == 1:
   reg = result1[0][0].decode()
   if reg != register:
    code = result1[0][1].decode()
   else:
    code = result1[0][1].decode()
 
  if len(result2) == 1:
   reg = result2[0][0].decode()
   if reg != register:
    code = result2[0][1].decode()
   else:
    code = result2[0][1].decode()
 else:
  code = "denied"   
   
 openseed.commit()
 mysearch.close()
 openseed.close()
 return str(code)

print("Content-type:text/html\r\n")

if action == "newkey":
 print(store_onetime(thetype,register,validusers))
if action == "getkey":
 print(update_key(thetype,register,validusers))
