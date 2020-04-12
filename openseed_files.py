#!/usr/bin/python

import subprocess
import sys
import os
sys.path.append("..")
import mysql.connector
import socketserver
import openseed_account as Account
import openseed_seedgenerator as Seed
import openseed_utils as Utils
#import steem_get as Get
#import steem_submit as Submit
#import leaderboard as LeaderBoard
import openseed_music as Music
import openseed_setup as Settings
import json
import time
from bottle import route, run, template, request

settings = Settings.get_settings()

@route('/img/<size>/<name>')
def display_image():
	return

@route('/')
def index():
	return template('<b>Hello {{name}}</b>!', name="you need to supply a command")


@route('/upload', method='POST')
def do_upload():
	devPub = request.forms.get('devPub')
	appPub = request.forms.get('appPub')
	cat = request.forms.get('category')
	thefile = request.files.get('data')

	if Account.check_appID(from_client["appPub"],from_client["devPub"]):
		name, ext = os.path.splitext(thefile.filename)
		save_path = get_save_path_for_category(cat)
		thefile.save(save_path) # appends upload.filename automatically
		Utils.png_and_pin(thefile.filename)
		return 'OK' 
	else:
		return 'error'
	
	

def get_save_path_for_category(category):
	path = ""
	if category == "image":
		path = "openseed/images/source"
	if category == "video":
		path = "openseed/videos/source"
	if category == "game":
		path = "openseed/games"
	if category == "music":
		path = "openseed/music/source"

	return path
	
run(host='0.0.0.0', port=8689)
