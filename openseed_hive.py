#!/usr/bin/python
import sys
import mysql.connector
import hashlib
import json
from hive import hive
from hive import wallet
import openseed_account as Account
sys.path.append("..")
import openseed_setup as Settings

settings = Settings.get_settings()
thenodes = ['anyx.io','api.hive.house','hive.anyx.io','hived.minnowsupportproject.org','hived.privex.io']
h = hive.Hive(nodes=thenodes)
w = wallet.Wallet
fix_thy_self = wallet.Wallet()

w.unlock(fix_thy_self,user_passphrase=settings["passphrase"])

postingKey = w.getPostingKeyForAccount(fix_thy_self,settings["hiveaccount"])
h.keys = postingKey
who = settings["hiveaccount"]


#!/usr/bin/python

import subprocess
import sys
import time
sys.path.append("..")
import mysql.connector
import json
from hive import hive
import openseed_music as Music
import openseed_ipfs as IPFS
import openseed_setup as Settings
import openseed_account as Account

settings = Settings.get_settings()
thenodes = ['anyx.io','api.hive.house','hive.anyx.io','hived.minnowsupportproject.org','hived.privex.io']
h = hive.Hive(nodes=thenodes)

songtype = "NA"
genre = "NA"
artist = "NA"
permlink = "NA"
ipfs = "NA"
img = "NA"
songtags = "NA"
duration = "0.00"
title = "New Song"


##############################
#
# Retrevial Functions
#
##############################



def get_post(author,permlink) :
	post = h.get_content(author,permlink)
	return '{"hive_post":{"author":"'+author+'","title":'+json.dumps(post["title"])+',"post":'+json.dumps(post["body"])+'}}'

def get_account(account):
	profile = '{"profile":"Not found"}'
	full_account = h.get_account(account)
	if full_account:
		profile = full_account["json_metadata"]
	return('{"username":"'+account+'","hive":'+profile+'}')

def get_full_account(account):
	profile = '{"profile":"Not found"}'
	full_account = h.get_account(account)
	if full_account:
		profile = json.dumps(full_account)
	return('{"username":"'+account+'","hive":'+profile+'}')

def get_connections(account):
	connections = []
	follows = []
	watching = []
	followers = h.get_followers(account,0,"",1000)
	following = h.get_following(account,0,"",1000)
	if str(followers).find("error") == -1:
		for flwrs in followers:
			follows.append(flwrs["follower"])
	if str(following).find("error") == -1:
		for flws in following:
			watching.append(flws["following"])

	for er in follows:
		for ing in watching:
			if er == ing:
				hiveaccount = json.loads(get_account(er))
				if "profile" in hiveaccount and hiveaccount["profile"] != "Not found":
					theName = er
					theAbout = ""
					theProfileImg = ""
					theBannerImg = ""
					
					if "name" in hiveaccount["profile"]:
						theName = hiveaccount["profile"]["name"]
					if "about" in hiveaccount["profile"]:
						theAbout = hiveaccount["profile"]["about"]
					if "profile_image" in hiveaccount["profile"]:
						theProfileImg = hiveaccount["profile"]["profile_image"]
					if "cover_image" in hiveaccount["profile"]:
						theBannerImg = hiveaccount["profile"]["cover_image"]

					data1 = '{"name":"'+theName+'","email":"","phone":"","profession":"","company":""}'
					data2 = '{"about":"","profile_img":"'+theProfileImg+'","banner":"'+theBannerImg+'"}'
					blank_p = '"profile":{"openseed":'+data1+',"extended":{},"appdata":{},"misc":{},"imports":{}}'
					connections.append('{"username":"'+er+'","linked":1,'+blank_p+'}')


	return(connections)


## Music specific functions (should be moved at some point ##

def local_search(author):
	openseed = mysql.connector.connect(
		host = "localhost",
		user = settings["ipfsuser"],
		password = settings["ipfspassword"],
		database = "ipfsstore"
		)
	mysearch = openseed.cursor()
	search = "SELECT * FROM `audio` WHERE `author`='"+str(author)+"'"
	mysearch.execute(search)
	result = len(mysearch.fetchall())
	mysearch.close()
	openseed.close()
	if result == 0:
		return("{New Artist}")
	else:
		return (Music.get_artist_tracks(author))


def search_music(author,limit) :
	#print(author,limit)
	local = local_search(author)
	activity = h.get_account_history(author,index_from = -1,limit = limit)
	for post_info in activity :
		if post_info != None:
			if post_info[1]["op"][0] == "comment" and post_info[1]['op'][1]['author'] == author:
				permlink = post_info[1]['op'][1]['permlink']
				title = post_info[1]['op'][1]['title']
				if str(post_info[1]["op"][1].keys()).find("json_metadata") != -1:
					if len(post_info[1]["op"][1]["json_metadata"]) > 5:
						metadata = json.loads(post_info[1]["op"][1]["json_metadata"])
						if metadata != '{"app":"threespeak/1.0"}' and metadata != '' and str(metadata.keys()).find("tags") != -1:
							tags = metadata["tags"]
							if tags != None:
								if str(tags).find("dsound") != -1:
									if str(metadata.keys()).find("audio") != -1:
										songtype = metadata["audio"]["type"]
										songtags = tags
										duration = metadata["audio"]["duration"]
										ipfs = metadata["audio"]["files"]["sound"]
										artist = author
										img = metadata["audio"]["files"]["cover"]
										genre = metadata["audio"]["genre"]
										IPFS.pin_and_record(ipfs,artist,title,permlink,img,songtype,genre,songtags,duration)
	return(local)

def search_history(user,limit):
	openseed = mysql.connector.connect(
		host = "localhost",
		user = settings["dbuser"],
		password = settings["dbpassword"],
		database = "openseed"
		)
	mysearch = openseed.cursor()
	search = "SELECT userId FROM `users` WHERE hive = %s"
	mysearch.execute(search,(user,))
	result = mysearch.fetchall()

	activity = h.get_account_history(user,index_from = -1,limit = limit)
	tags = ""
	for post_info in activity :
		if post_info != None:
			if post_info[1]["op"][0] == "comment" and post_info[1]['op'][1]['author'] == user:
				permlink = post_info[1]['op'][1]['permlink']
				title = post_info[1]['op'][1]['title']
				if str(post_info[1]["op"][1].keys()).find("json_metadata") != -1:
					if len(post_info[1]["op"][1]["json_metadata"]) > 4:
						metadata = json.loads(post_info[1]["op"][1]["json_metadata"])
						if metadata != '' and str(metadata.keys()).find("tags") != -1:
							tags = metadata["tags"]
				if len(title) > 2:
					data = '{"post":{"title":"'+title+'","permlink":"'+permlink+'","tags":"'+str(tags)+'"}}'
					Account.update_history(str(result[0][0].replace('\x00',"")),9,"hive",str(data))
				break


	mysearch.close()
	openseed.close()

	return


######################################
#
# Submission functions. 
#
######################################

def memo(username,hivename,code):
	openseed = mysql.connector.connect(
	host = "localhost",
	user = settings["dbuser"],
	password = settings["dbpassword"],
	database = "openseed"
	)
	service_type = "hive"
	codesearch = openseed.cursor()
	link = "Thank you for registering your hive account on OpenSeed. Please copy and paste this link : http://142.93.27.131:8675/account.py?act=verify&hivename="+str(hivename)+"&username="+str(username)+"&onetime="+str(code)+" into your address bar to finish the process"
	tamount = 0.001
	h.commit.transfer(to=hivename,amount=tamount,asset='hive',memo=link,account=who)
	update = "UPDATE `onetime` SET `sent` = TRUE WHERE `type` = '"+service_type+"' AND `user` = '"+username+"'"
	codesearch.execute(update)
	openseed.commit()
	codesearch.close()
	openseed.close()

def create_json(devID,appID,user,theid,data):
	
	post = '{"appId":"'+str(appId)+'","devId":"'+str(devId)+'","userId":"'+str(userId)+'","score":"'+str(score)+'"}'
	h.commit.custom_json(id=theid, json=post)

def create_post(devID,appID,publicID,title,data):
	
	return

def like_post(token,author,post,percent = 30):
	w.unlock(fix_thy_self,user_passphrase=settings["passphrase"])
	print("voting on ",post)
	poster = token
	if token != who:
		poster = json.loads(Account.user_from_id(token))["hive"]
	print("as ",poster)
	print("at ",percent)
	already_voted = -1
	# Gets votes on the post
	result = h.get_active_votes(author, post)
	if result and poster != None and poster != "":
		# We run through the votes to make sure we haven't already voted on this post
		for vote in result:
			if vote['voter'] == poster:
				already_voted = 1
				break
			else:
				already_voted = 0

		if already_voted == 0:
			identifier = ('@'+author+'/'+post)
			h.commit.vote(identifier, float(percent), poster)
			return('{"liked_hive_post":{"response":"voted","weight":'+str(percent)+',"post":"'+post+'"}}')
		else:
			return('{"liked_hive_post":{"response":"already voted","weight":"error","post":"'+post+'"}}')
		
		return('{"liked_hive_post":{"response":"error","weight":"error","post":"error"}}')


def post_comment(token,author,post,body):
	w.unlock(fix_thy_self,user_passphrase=settings["passphrase"])
	response = '{"hive_comment":{"response":"error","post":"error"}}'
	print("commenting on ",post)
	poster = token
	if token != who:
		poster = json.loads(Account.user_from_id(token))["hive"]
	if poster == None or poster == "":
		poster = who
		body += "\n "+json.loads(Account.user_from_id(token))["user"]+" on ODESI"
	reply_identifier = '/'.join([author,post])
	print(reply_identifier)
	h.commit.post(title='', body=body, author=poster, permlink='',reply_identifier=reply_identifier) 
	response = '{"hive_comment":{"response":"added","post":"'+post+'"}}'
	return response

def openseed_post(author,post,body,title,json):
	h.commit.post(title=title, body=body, author=who, permlink='') 
	print("adding post")
	return

def payment(hiveaccount,to_account,amount,data,postingkey):
	if w.getActiveKeyForAccount(hiveaccount):
		h.keys = w.getActiveKeyForAccount(hiveaccount)
	else:
		w.addPrivateKey(postingkey)
		h.keys = postingkey

	receipt = str(data)+' via OpenSeed'
	asset = 'HIVE'
	if amount.split(",")[1].split("]")[0] == 1:
		asset = 'HBD'
	payout = amount.split(",")[0].split("[")[1]
	h.commit.transfer(to=to_account,amount=float(payout),asset=asset,memo=receipt,account=hiveaccount)
	return('{"payment":{"sent":"'+payout+'","in":"'+asset+'","to:"'+to_account+'"}}')

def check_account(account,postkey):
	hiveaccount = w.getAccountFromPrivateKey(fix_thy_self,postkey)
	if account == hiveaccount:
		return 1
	else:
		return 0
	
def store_key(account,key):
	w.addPrivateKey(fix_thy_self,key)
	return 1 
	
def import_account(account,masterpass):
	
	return

def openseed_interconnect(openseed,acc,postkey,storekeys,importprofile):
	token = ""
	response = '{"interconnect":"error","account_auth":"error","keystored":False}'
	if check_account(acc,postkey) == 1:
		exists = Account.check_db(acc,"users")
		if exists !=0:
			print("user exists")
			print("checking if hive account is connected to an openseed account")
			verifing = json.loads(check_link(openseed,acc))
			if verifing["openseed"] == 1 and verifing["openseed"] == verifing["hive"]:
				token = json.loads(Account.id_from_user(openseed))["id"]
				response = '{"interconnect":"connected","account_auth":"openseed","keystored":'+str(storekeys)+'}'
			elif verifing["openseed"] == 0 and verifing["hive"] == 1:
				response = '{"interconnect":"Hive account in use","account_auth":"error","keystored":false}'
			elif verifing["openseed"] == 1 and verifing["hive"] == 0:
				token = json.loads(Account.id_from_user(openseed))["id"]
				if update_account(openseed,acc) == 1:
					if store_key(acc,postkey) == 1:
						set_delegation(acc,"openseed")
					if storekeys == False:
						flush_account(acc)
					response = '{"interconnect":"connected","account_auth":"openseed","keystored":'+str(storekeys)+'}'
		else:
			new = json.loads(Account.external_user(acc,postkey,"hive"))
			Account.create_default_profile(new["token"],new["username"],"")
			token = new["token"]
			update_account(new["username"],new["username"])
				
		if importprofile == True and token != "":
			import_profile(token,acc)
			
	return response

def import_profile(token,hiveaccount):

	openseed = json.loads("{"+Account.get_profile(json.loads(Account.user_from_id(token))["user"])+'}')
	
	od1 = openseed["profile"]["openseed"]
	od2 = openseed["profile"]["extended"]
	banner = ""
	profile_image = ""
	name = od1["name"]
	if "banner" in od2:
		banner = od2["banner"]
	if "profile_img" in od2:
		profile_image = od2["profile_img"]	
	about = od2["about"]
	email = od1["email"]
	phone = od1["phone"]
	profession = od1["profession"]
	company = od1["company"]
	
	hive = json.loads(get_account(hiveaccount))
	pfile = ""
	if "profile" in hive:
		pfile = hive["profile"]
	if "app" in hive:
		pfile = hive["app"]["profile"]
		
	if "name" in pfile:
		name = pfile["name"]
	if "about" in pfile:
		about = pfile["about"]
	if "profile_image" in pfile:
		profile_image = pfile["profile_image"]
	if "cover_image" in pfile:
		banner = pfile["cover_image"]
		
	
	data1 = '{"name":"'+name+'","email":"'+email+'","phone":"'+phone+'","profession":"'+profession+'","company":"'+company+'"}'
	data2 = '{"about":"'+about+'","profile_img":"'+profile_image+'","banner":"'+banner+'"}'

	
	Account.set_profile(token,data1,data2,"","","",1)

	return			

def check_in_use(hiveaccount):
	db = mysql.connector.connect(
		host = "localhost",
		user = settings["dbuser"],
		password = settings["dbpassword"],
		database = "openseed"
		)
	mycursor = db.cursor()
	
	find_hive = "SELECT username,hive FROM `users` WHERE hive = %s"
	hive_val = (hive,)
	mycursor.execute(find_hive,hive_val)
	hive_result = mycursor.fetchall()	
	db.close()
	
	return '{"hive_account":'+hiveaccount+',"in_use":'+str(len(hive_result))+'}'		
	
def check_verified(openseed):
	
	db = mysql.connector.connect(
		host = "localhost",
		user = settings["dbuser"],
		password = settings["dbpassword"],
		database = "openseed"
		)
	mycursor = db.cursor()
	
	find_openseed = "SELECT username,hive FROM `users` WHERE username = %s AND hive IS NOT NULL"
	openseed_val = (openseed,)
	mycursor.execute(find_openseed,openseed_val)
	openseed_result = mycursor.fetchall()

	if len(openseed_result) != 0:
		return '{"openseed":"'+openseed+'","hive":"'+openseed_result[0][1]+'"}'
	else:
		return	'{"openseed":"'+openseed+'","hive":"not connected"}'

def check_link(openseed,hive):
	
	db = mysql.connector.connect(
		host = "localhost",
		user = settings["dbuser"],
		password = settings["dbpassword"],
		database = "openseed"
		)
	mycursor = db.cursor()
	
	find_openseed = "SELECT username,hive FROM `users` WHERE username = %s"
	openseed_val = (openseed,)
	mycursor.execute(find_openseed,openseed_val)
	
	openseed_result = mycursor.fetchall()
	find_hive = "SELECT username,hive FROM `users` WHERE hive = %s"
	hive_val = (hive,)
	mycursor.execute(find_hive,hive_val)
	hive_result = mycursor.fetchall()	
	db.close()
	
	return '{"openseed":'+str(len(openseed_result))+',"hive":'+str(len(hive_result))+'}'

def find_keys_by_accountname(account):

	return

def set_delegation(acc, hiveapp, privatekey=""):
	postingKey = w.getPostingKeyForAccount(fix_thy_self,acc)
	findapp = json.loads(Hive.get_full_account(acc)["posting"]["account_auths"])
	if str(findapp).find("['openseed', 1]") == -1:
		h.keys = postingKey
		who = acc
		h.commit.allow(hiveapp,permission="posting",account=acc)
	
	return '{delegation:{"account":"'+acc+'","rights":"posting","to":"'+hiveapp+'"}'

def remove_delegation(acc, hiveapp, privatekey=""):
	postingKey = w.getPostingKeyForAccount(fix_thy_self,acc)
	h.keys = postingKey
	who = acc
	h.commit.disallow(hiveapp,permission="posting",account=acc)
	
	return '{delegation:{"account":"'+acc+'","rights":"removed","to":"'+hiveapp+'"}'

def flush_account(hiveaccount):
	w.removeAccount(fix_thy_self,hiveaccount)
	return('{"removed":"'+hiveaccount+'"}')
	
def update_account(openseed,account):
	db = mysql.connector.connect(
	host = "localhost",
	user = settings["dbuser"],
	password = settings["dbpassword"],
	database = "openseed"
	)
	
	update = db.cursor()
	update_string = "UPDATE `users` SET hive = %s WHERE username = %s"
	val = (account,openseed)
	update.execute(update_string,val)
	db.commit()
	update.close()
	db.close()
	return 1

