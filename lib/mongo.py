#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo import TEXT
from pymongo import ASCENDING
from random import randint

conn = None
videos = None
subtitles = None

SKIP_AMOUNT = 1000

def init():
	global conn, videos, subtitles, db

	conn = MongoClient()	
	db = conn['snippetDb']
	subtitles = db.subtitles
	videos = db.videos
	makeIndexOnSnippetDb()

def dropAndReconnect():
	db = conn['snippetDb']
	db.videos.drop()	
	db.subtitles.drop()
	subtitles = db.subtitles
	videos = db.videos
	makeIndexOnSnippetDb()

def saveUrl(tinyurl):
	try:
		videos.insert_one({'youtubeid': tinyurl, 'randompicked': "0",'infoadded': "0"})
	except:
		print "already exists."

def getRandomID(skip=True):
	skipAmount = 0
	
	if skip:
		skipAmount = randint(0, SKIP_AMOUNT)

	cursor = videos.find_one({'randompicked': 0},{"youtubeid": 1}, skip = skipAmount) # $skip: XXX
	
	if not cursor:
		return getRandomID(False)

	return cursor['youtubeid']
	

def pickUpdate(tinyurl):
	videos.update_one({'youtubeid': tinyurl}, {"$set": {'randompicked': "1"}})


def getNotPicked():
	count = videos.find({'randompicked': "0"}).count()
	return count


def titleUpdate(title, tinyurl):
	videos.update_one({'youtubeid': tinyurl}, {"$set": {'title': title}})


def captionUpdate(caption, tinyurl):
	videos.update_one({'youtubeid': tinyurl}, {"$set": {'caption': caption}})


def deleteItem(tinyurl):
	videos.delete_one({'youtubeid': tinyurl})


def infoUpdate(tinyurl):
	videos.update_one({'youtubeid': tinyurl}, {"$set": {'infoadded': "1"}})


def updateTimecodes(tinyurl, startTime, duration, content):
	subtitles.insert_one({
		'youtubeid': tinyurl,
		'starttime': startTime,
		'duration': duration,
		'content': content
	})

def makeIndex():
	db.subtitles.ensure_index([("content", TEXT)])
	db.subtitles.ensure_index(("youtubeid"), ASCENDING)
	db.videos.ensure_index(("youtubeid"), unique = True)

def makeIndexOnSnippetDb():
	db.videos.ensure_index(("filename"), unique = True)

def findKeyword(keyword):
	cursor = db.subtitles.find({ "$text": { "$search": keyword}}).sort('youtubeid', ASCENDING)
	return cursor
	
def updateDate(tinyurl, date):
	videos.update_one({'youtubeid': tinyurl}, {"$set": {'date': date}})

def getUniqueTinys():
	cursor = db.videos.find({}).sort('youtubeid', ASCENDING)
	return cursor

def updateDate(tinyurl, width, height, aspectRatio):
	videos.update_one({'youtubeid': tinyurl}, {"$set": {'width': width}})
	videos.updade_one({'youtubeid': tinyurl}, {"$set": {'height': height}})
	videos.updade_one({'youtubeid': tinyurl}, {"$set": {'aspectRatio': aspectRatio}})

def saveSnippet(topic, filename, duration, tinyurl):
	videos.insert_one({'filename': filename, 'youtubeid': tinyurl, 'topic': topic, 'duration': duration, 'randompicked': "0"})

def snippetPicker(topic, mode):
	if mode == 1:
		SKIP_RANGE = videos.find({'topic': topic,'randompicked': "0", 'duration': {"$lte": "3"}}).count()
		print "SKIP_RANGE is:"+str(SKIP_RANGE)
		skipAmount = randint(0, SKIP_RANGE)
		if (skipAmount == 0):
			skipAmount = 1
		print "skipAmount is: "+str(skipAmount) 
		cursor = db.videos.find_one({'topic': topic,'randompicked': "0", 'duration': {"$lte": "3"}}, {'filename': 1, 'duration': 1, 'youtubeid': 1}, skip = skipAmount-1)
		return cursor

	elif mode == 2:
		SKIP_RANGE = videos.find({'topic': topic, 'randompicked': "0", 'duration': {"$gte": "5"}}).count()
		#print "SKIP_RANGE is:"+str(SKIP_RANGE)
		skipAmount = randint(0, SKIP_RANGE)
		if (skipAmount == 0):
			skipAmount = 1
		#print "skipAmount is: "+str(skipAmount) 
		cursor = db.videos.find_one({'topic': topic, 'randompicked': "0", 'duration': {"$gte": "5"}}, {'filename': 1, 'duration': 1, 'youtubeid': 1}, skip = skipAmount-1)
		return cursor

	elif mode == 3:
		SKIP_RANGE = videos.find({'topic': topic,'randompicked': "0", 'duration': {"$gte": "6"}}).count()
		print "SKIP_RANGE is:"+str(SKIP_RANGE)
		skipAmount = randint(0, SKIP_RANGE)
		if (skipAmount == 0):
			skipAmount = 1
		print "skipAmount is: "+str(skipAmount) 
		cursor = db.videos.find_one({'topic': topic,'randompicked': "0", 'duration': {"$lte": "6"}}, {'filename': 1, 'duration': 1, 'youtubeid': 1}, skip = skipAmount-1)
		return cursor

	

def pickUpdateFilename(filename):
	videos.update_one({'filename': filename}, {"$set": {'randompicked': "1"}})

def snippetFitter(topic, duration):
	SKIP_RANGE = videos.find({'topic': topic, 'duration': duration, 'randompicked': "0"}).count()
	print "SKIP_RANGE is:"+str(SKIP_RANGE)
	skipAmount = randint(0, SKIP_RANGE)
	print "skipAmount is: "+str(skipAmount) 
	if (skipAmount == 0):
		skipAmount = 1
	cursor = db.videos.find_one({'randompicked': "0", 'topic': topic, 'duration': duration}, {'filename': 1, 'duration': 1, 'youtubeid': 1}, skip = skipAmount-1)
	return cursor
