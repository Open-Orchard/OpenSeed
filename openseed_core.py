#!/usr/bin/python3

import subprocess
import sys
import os
sys.path.append("..")
import mysql.connector
import socketserver
import openseed_account as Account
import openseed_seedgenerator as Seed
import openseed_utils as Utils
import hive_get as Get
import hive_submit as Submit
#import leaderboard as LeaderBoard
import openseed_music as Music
import openseed_setup as Settings
import json
import time
from bottle import route, run, template, request, static_file

settings = Settings.get_settings()


def message(data):

	try:
		from_client = json.loads(data)
	except:
		return '{"server":"not json"}'
	else:		
		action = from_client["act"]
		if Account.check_appID(from_client["appPub"],from_client["devPub"]):
			app = from_client["appPub"]
			dev = from_client["devPub"]

			#####################################################
			#
			#  Account Section
			#
			#####################################################

			if action == "accountcheck":
				response = Account.accountCheck(from_client["username"],from_client["passphrase"])
			elif action == "creatorcheck":
				response = Account.creator_check(from_client["steem"])
			elif action == "create":
				response = Account.create_user(from_client["username"],from_client["passphrase"],from_client["email"])
			elif action == "link":
				response = Account.Steem.link(from_client["username"],from_client["steemname"])
				if response:
					Submit.memo(from_client["username"],from_client["steemname"],response)
			elif action == "create_creator":
				response = Account.create_creator(from_client["devName"],from_client["contactName"],from_client["contactEmail"],from_client["steem"])
			elif action == "set_profile":
				response = Account.set_profile(from_client["token"],from_client["data1"],from_client["data2"],
					from_client["data3"],from_client["data4"],from_client["data5"],from_client["type"])
			elif action == "get_status":
				response = Account.get_status(from_client["account"])
			elif action == "set_status":
				response = Account.set_status(from_client["appPub"],from_client["token"],from_client["status"])
			elif action == "get_history":
				response = Account.get_history(from_client["account"],from_client["apprange"],from_client["count"])
			elif action == "update_history":
				response = Account.update_history(from_client["account"],from_client["type"],from_client["appPub"],from_client["data"])

			#####################################################
			#
			#  Hive Section
			#
			#####################################################

			elif action == "payment":
				response = Submit.payment(from_client["hiveaccount"],from_client["to"],from_client["amount"],from_client["for"],from_client["postingkey"])
			elif action == "flush":
				response = Submit.flush(from_client["hiveaccount"])
			elif action == "verify":
				response = Account.Steem.verify(from_client["username"],from_client["onetime"])

			#####################################################
			#
			#  Games Section
			#
			#####################################################

			elif action == "toleaderboard":
				response = LeaderBoard.update_leaderboard(dev,app,from_client["username"],from_client["data"],from_client["steem"],from_client["postingkey"])
			elif action == "getleaderboard":
				response = LeaderBoard.get_leaderboard(dev,app)

			#####################################################
			#
			#  Music Section
			#
			#####################################################

			elif action == "music":
				response = Music.get_curated_music(from_client["curator"])
			elif action == "music_json":
				response = Music.get_curated_music_json(from_client["curator"])
			elif action == "post":
				response = Get.get_post(from_client["author"],from_client["permlink"])
			elif action == "artist_search":
				response = Get.search_music(from_client["author"],10000)
			elif action == "getaccount":
				response = Get.get_account(from_client["account"])
			elif action == "getfullaccount":
				response = Get.get_full_account(from_client["account"])
			elif action == "newmusicians":
				response = Music.get_new_artists()
			elif action == "newtracks":
				response = Music.get_new_tracks()
			elif action == "newtracks_json":
				response = Music.get_new_tracks_json()
			elif action == "genres":
				response = Music.get_genres()
			elif action == "genre":
				response = Music.get_genre_tracks(from_client["genre"])
			elif action == "genre_json":
				response = Music.get_genre_tracks_json(from_client["genre"],from_client["count"])
			elif action == "getArtistTracks":
				response = Music.get_artist_tracks_json(from_client["author"],from_client["count"])
			elif action == "getTracks":
				response = Music.get_tracks_json(from_client["start"],from_client["count"])

			#####################################################
			#
			#  Connections Section
			#
			#####################################################

			elif action == "hive_connections":
		    		response = Connections.get_steem_connections(from_client["hive"])
			elif action == "openseed_connections":
				response = Connections.get_openseed_connections(from_client["account"],from_client["hive"])
			elif action == "get_profile":
				response = "{"+Connections.user_profile(from_client["account"])+"}"
			elif action == "get_requests":
				response = Connections.get_requests(from_client["token"],from_client["count"])
			elif action == "send_request":
				response = Connections.connection_request(from_client["token"],from_client["account"],"request",app)
			elif action == "set_request":
				response = Connections.connection_request(from_client["token"],from_client["account"],from_client["response"],app)
			elif action == "request_status":
				response = Connections.request_status(from_client["token"],from_client["account"])

			#####################################################
			#
			#  Chat Section
			#
			#####################################################

			elif action == "get_conversations":
				response = Chat.get_conversations(from_client["token"])
			elif action == "create_chatroom":
				response = Chat.create_chatroom(from_client["token"],from_client["title"],from_client["attendees"],app)
			elif action == "get_chat_history":
				response = Chat.get_chat_history(from_client["token"],from_client["room"],from_client["count"],from_client["last"])
			elif action == "get_chat":
				response = Chat.get_chat(from_client["token"],from_client["room"],from_client["last"])
			elif action == "send_chat":
				response = Chat.send_chat(from_client["token"],from_client["room"],from_client["message"],app)
			elif action == "find_room_by_attendees":
				response = Chat.find_attendees(from_client["token"],from_client["attendees"],from_client["create"],app)

			elif action == "set_key":
				response = OneTime.store_onetime(from_client["type"],from_client["register"],from_client["validusers"])
			elif action == "get_key":
				response = OneTime.get_key(from_client["thetype"],from_client["token"],from_client["room"])

			# Heart Beat #	
			elif action == "heartbeat":
				response = "Online"

			# Utils #
			elif action =="get_image":
				response = Utils.get_image(False,from_client["image"],from_client["thetype"],from_client["size"])
				
			else:
				response = "App rejected"

