#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

conn = None
c = None

def init(dbName):
	global conn, c

	conn = sqlite3.connect(dbName + '.db')
	c = conn.cursor()

def saveUrl(tinyurl):
	c.execute("""SELECT NOT EXISTS(SELECT * FROM urls WHERE youtubeid=?)""", (tinyurl,))
	
	if (c.fetchone()[0]):
		c.execute("""INSERT INTO urls VALUES (?,"0","-","-","0","-","0", "-")""", (tinyurl,))
		conn.commit()


def createDb():
	c.execute("""DROP TABLE IF EXISTS urls""")
	c.execute("""CREATE TABLE urls (youtubeid text,randompicked int, title text, description text, infoadded int, subtitle text, embedded int, textFile text);""")

def getRandomID():
	c.execute("""SELECT youtubeid FROM urls WHERE randompicked = 0 ORDER BY RANDOM() LIMIT 1""")		
	return c.fetchone()[0]	

def pickUpdate(tinyurl):
	c.execute("""UPDATE urls SET randompicked = 1 WHERE youtubeid=?""", (tinyurl,))
	conn.commit()

def titleUpdate(title,description,tinyurl):
	c.execute("""UPDATE urls SET title=? WHERE youtubeid=?""",(title,tinyurl,))
	c.execute("""UPDATE urls SET description=? WHERE youtubeid=?""",(description,tinyurl,))
	conn.commit()

def getDbSize():
	c.execute("""SELECT COUNT(*) FROM urls""")
	return c.fetchone()[0]

def getNotPicked():
	c.execute("""SELECT COUNT(*) FROM urls WHERE randompicked = 0""")
	return c.fetchone()[0]

def getRandomIDforInfo():
	c.execute("""SELECT youtubeid FROM urls WHERE infoadded = 0 ORDER BY RANDOM() LIMIT 1""")		
	return c.fetchone()[0]

def infoUpdate(tinyurl):
	c.execute("""UPDATE urls SET infoadded = 1 WHERE youtubeid=?""", (tinyurl,))
	conn.commit()

def deleteRow(tinyurl):
	c.execute("""DELETE FROM urls where youtubeid=?""", (tinyurl,))
	conn.commit()

def captionUpdate(caption,tinyurl):
	c.execute("""UPDATE urls SET embedded = 1 WHERE youtubeid=?""", (tinyurl,))
	c.execute("""UPDATE urls SET subtitle=? WHERE youtubeid=?""", (caption, tinyurl,))
	conn.commit()
	print "sub saved"

def grabCaption(tinyurl):
	c.execute("""SELECT subtitle FROM urls WHERE youtubeid=?""",(tinyurl,))
	return c.fetchone()[0]

def textUpdate(textFile, tinyurl):
	c.execute("""UPDATE urls SET textFile=? WHERE youtubeid=?""", (textFile, tinyurl,))
	conn.commit()

def grabText(tinyurl):
	c.execute("""SELECT textFile FROM urls WHERE youtubeid=?""", (tinyurl,))
	return c.fetchone()[0]

