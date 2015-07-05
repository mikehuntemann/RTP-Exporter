#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys 
import os
import shlex
import subprocess
import re
from random import randint

sys.path.append(os.path.abspath("lib"))
import mongo

#topic collections
collection = []
nextTopic = []

#.txt files
exportfiles = []

#total loop length in seconds
totalTime = 0

#individual Peak Times
channelTIME = 0
channelDONE = False

durationChannelONE = 0

#Multichannel settings
channelSelectONE = 0
channelSelectTWO = 0
otherChannels = []
roundCounter = 1

#default settings
breakDuration = 1
totalChannels = 5

#automatic screenExtender
screenExtender1 = 0
screenExtender2 = 0


def channelSetup(totalChannels):
	global screenExtender1, screenExtender2
	
	print "\ncreating exportfiles:"
	for channel in range(0, totalChannels):
		otherChannels.append(channel)
		filename = "channelFile"+str(channel+1)+".txt"
		exportfiles.append(filename)
		print "--> "+filename
	
	#gerade plus 1 alle zwei zahlen
	if (totalChannels % 2 == 0):
		base = totalChannels - 4
		if (base != 0):
			times = base / 2
			screenExtender1 = 1+times		
			print "screenExtender1.0: "+str(screenExtender1)
	 	else:
	 		screenExtender1 = 1
	 		print "screenExtender1.1: "+str(screenExtender1)
	
	#ungerade plus 1 alle zeit zahlen
	elif (totalChannels % 2 == 1):
		if (totalChannels > 5):
			base = totalChannels - 5
			times = base / 2
			screenExtender1 = 1+times
			print "screenExtender1.2: "+str(screenExtender1)
		else:
	 		screenExtender1 = 1
	 		print "screenExtender1.3: "+str(screenExtender1)
	else:
	 	screenExtender1 = 0
	 	print "screenExtender1.4: "+str(screenExtender1)

	#plus 1 ab 6
	if (totalChannels > 5):
	 	times = totalChannels - 5
	 	screenExtender2 = times
	 	print "screenExtender2: "+str(screenExtender2)
	else:
	 	screenExtender2 = 0
	 	print "screenExtender2: "+str(screenExtender2)


def clearExportfiles():
	for filename in os.listdir("/Users/MH/Projects/Youtube-Crawler/exports/batchfiles/"):
			if filename.endswith(".txt"):
				print filename +" found."
				os.remove("/Users/MH/Projects/Youtube-Crawler/exports/batchfiles/"+filename)
				print filename + " removed."


def clearOutputfiles():
	for filename in os.listdir("/Users/MH/Projects/Youtube-Crawler/exports/output/"):
			if filename.endswith(".mp4"):
				print filename +" found."
				os.remove("/Users/MH/Projects/Youtube-Crawler/exports/output/"+filename)
				print filename + " removed."
			else:
				print "no files found."


def loadSnippetsToDb():
	print "\nsearching for source directories."

	for sourceDir in os.listdir("exports/snippets/"):
		if sourceDir.startswith("."):
			print "--> "+sourceDir + " ignored."
		else:
			#order cleanup
			sourceDir = sourceDir.split("_")[-1]

			collection.append(sourceDir)
			print "--> "+sourceDir + " added to collection."
			nextTopic.append(sourceDir)
	
	indexCounter = 1
	for topic in collection:
		print "\nworking in "+topic+" directory."
		snippetCounter = 0
		for filename in os.listdir("exports/snippets/"+str(indexCounter)+"_"+topic+"/"):
			if filename.endswith(".mp4"):
				# filename structure: 0AnzzuOuw4w_00-00-39-5.mp4
				tinyurl = re.findall("\w{11}", filename)[0]
				#[-1:] = last char in a string
				duration = filename.split(".")[0][-1:]
				try:
					mongo.saveSnippet(topic, filename, duration, tinyurl)
					snippetCounter += 1
				except:
					pass
			else:
				print filename+" is no .mp4 file."
		print str(snippetCounter)+" snippets available for "+topic
		indexCounter += 1
	print "\ndone adding content to mongodb."
	contentSize = mongo.getNotPicked()
	print "a total of "+str(contentSize)+" snippets are available." 

def makeFiles1():
	topic = "ebola"
	global roundCounter, totalChannels
	global screenExtender1, screenExtender2
	print "working on topic: "+topic+"." 
	print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		# if topic is firsttopic do phase 1
		#phase 1:
	if (roundCounter == 1):
		number = screenExtender2+3
		modeTHREE(topic, phaseLength = totalTime + 60, activeChannels = number, mode = 3, breaks = True, blacks = True)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"


def makeFiles():
	global roundCounter, totalChannels
	global screenExtender1, screenExtender2
	
	for topic in collection:
		print "working on topic: "+topic+"." 
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		# if topic is firsttopic do phase 1
		#phase 1:
		if (roundCounter == 1):
			modeONE(topic, phaseLength = 30, activeChannels =  screenExtender1, mode = 1, breaks = False, blacks = True)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
			#phase 2:
			modeONE(topic, phaseLength = totalTime + 60, activeChannels = screenExtender1+1, mode = 1, breaks = False, blacks = True)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		else:
			modeONE(topic, phaseLength = totalTime + 60, activeChannels = screenExtender1+1, mode = 1, breaks = False, blacks = True)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		#phase 3:
		modeTWO(topic, phaseLength = totalTime + 30, activeChannels = totalChannels, mode = 2, breaks = False, blacks = False)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		#phase 4:
		if (roundCounter != 5):
			modeTHREE(topic, phaseLength = totalTime + 30, activeChannels = screenExtender2+3, mode = 3, breaks = True, blacks = True)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
			#phase 5:
			modeTHREE(topic, phaseLength = totalTime + 60, activeChannels = screenExtender1+1, mode = 3, breaks = True, blacks = True)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
			roundCounter += 1
		else:
			modeONE(topic, phaseLength = totalTime + 60, activeChannels = screenExtender1+1, mode = 1, breaks = False, blacks = True)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
			modeONE(topic, phaseLength = 30, activeChannels =  screenExtender1, mode = 1, breaks = False, blacks = True)
			print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
	
	print "Total project length is "+ str(totalTime)+" seconds."
	print "file done."


def modeTWO(topic, phaseLength, activeChannels, mode, breaks, blacks):
	global totalTime, channelTIME
	global channelDONE
	global durationChannelONE
	global channelSelectONE, channelSelectTWO
	global diffenceBlack
	global nextTopic
	
	timeDifference = phaseLength - totalTime
	

	print "----> entering modeTWO."
	print "totalTime is:"
	print totalTime
	print "phaseLength:"
	print phaseLength
	maxDuration = phaseLength-totalTime-3
	print "PEAKduration is: "+str(phaseLength-totalTime)
	counter = 0
	if (counter != totalChannels):
		for each in otherChannels:
			print "counter is: "+str(counter)
			channelDONE = False
			channelTIME = 0
			print "working on channel "+str(each+1)
			while (channelDONE == False):
				print "channelTIME is: "+str(channelTIME)
				durationDifference = (phaseLength - totalTime) - channelTIME
				print "durationDifference is "+str(durationDifference)
				if (durationDifference > 5):
					dataset1 = mongo.snippetPicker(topic, mode)
					if dataset1 is not None:
						durationChannelONE = snippetProcessing(topic, dataset1, each, True)
						channelTIME += durationChannelONE
					else:
						print "no more snippets in mongodb."
				else:
					if (durationDifference != 0):
						durationDifference = str(durationDifference)
						print "preparing last snippets for channel 1"
						dataset1 = mongo.snippetFitter(topic, durationDifference)
						if dataset1 is not None:
							snippetProcessing(topic, dataset1, each, False)
							print "added fitting snipped\ndone with channelONE."
							print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
							channelDONE = True
							counter += 1
						else:
							print "couldn't find a fitting snippet for channel 1."
					else:
						print "already fitting\ndone with channelONE."
						print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
						channelDONE = True
						counter += 1
	print "all channels are done with peak sequence."
	totalTime += timeDifference



def modeTHREE(topic, phaseLength, activeChannels, mode, breaks, blacks):
	print "----> entering modeTHREE."
	global totalTime
	global durationChannelONE
	global channelSelectONE, channelSelectTWO
	global diffenceBlack
	global roundCounter
	
	print "activeChannels: "+str(activeChannels)
	oldTopic = (activeChannels / 2) + 1
	print "oldTopic: "+str(oldTopic)
	newTopic = activeChannels - oldTopic
	print "newTopic: "+str(newTopic)
	timeDifference = phaseLength - totalTime

	while (totalTime < phaseLength):
		print "totalTime: "+str(totalTime)
		print "phaseLength: "+str(phaseLength)
		print "timeDifference: "+str(timeDifference)
		channelSelectONE = channelSelectTWO

		channelsPicked = []
		
		channelSelect = randint(0, activeChannels-1)
		print channelSelect
		channelsPicked.append(channelSelect)
		print channelsPicked
		print "\n"+str(oldTopic)+" channels active for current topic."
		dataset = mongo.snippetPicker(topic, mode)
		durationChannelONE = snippetProcessing(topic, dataset, channelSelect, True)
		print "writing snippet on channel "+str(channelSelect+1)+"."

		for channel in range(0, oldTopic-1):
			print "\nold loop -----> "+str(channel)
			newChannelSelect = randint(0, totalChannels-1)
			print newChannelSelect
			while (newChannelSelect in channelsPicked):
				newChannelSelect = randint(0, totalChannels-1)
			print channelsPicked
			print newChannelSelect
			print "writing snippet on channel "+str(newChannelSelect+1)+"."
			channelsPicked.append(newChannelSelect)
			durationONE = str(durationChannelONE)
			dataset = mongo.snippetFill(topic, durationONE)
			if dataset is not None:
				durationFill = snippetProcessing(topic, dataset, newChannelSelect, True)
				blackDuration = durationChannelONE - durationFill
				if (blackDuration != 0):
					blacksAdder(blacks, blackDuration, newChannelSelect)
				else:
					print "no black fills needed."
			else:
				print "not enough snippets for snippetFill."
		
	
		for channel in range(0, newTopic):
			print "\nnew loop -----> "+str(channel)
			newChannelSelect = randint(0, totalChannels-1)
			print channelsPicked
			print newChannelSelect
			while (newChannelSelect in channelsPicked):
				newChannelSelect = randint(0, totalChannels-1)
			print "writing snippet on channel "+str(newChannelSelect+1)+"."
			channelsPicked.append(newChannelSelect)
			print channelsPicked
			print newChannelSelect
			nextONE = nextTopic[roundCounter]
			dataset = mongo.snippetFill(nextONE, durationONE)
			if dataset is not None:
				print "checkpoint pre processing"
				durationFill = snippetProcessing(nextONE, dataset, newChannelSelect, True)
				blackDuration = durationChannelONE - durationFill
				if (blackDuration != 0):
					blacksAdder(blacks, blackDuration, newChannelSelect)
				else:
					print "no black fills needed."
			else:
				print "not enough snippets for snippetFill."
		
		print "emptyChannel checkpoint."
		print channelsPicked
		for emptyChannel in range(0, totalChannels):
				if (emptyChannel not in channelsPicked):
					print "pre blacks added, emptyChannel."
					blacksAdder(blacks, durationChannelONE, emptyChannel)

		totalTime += durationChannelONE
		breaksToAll(breaks, breakDuration)					




def modeONE(topic, phaseLength, activeChannels, mode, breaks, blacks):
	print "----> entering modeONE."
	global totalTime
	global durationChannelONE
	global channelSelectONE, channelSelectTWO
	global diffenceBlack
	
	timeDifference = phaseLength - totalTime

	while (totalTime < phaseLength):
		print "totalTime: "+str(totalTime)
		print "phaseLength: "+str(phaseLength)
		print "timeDifference: "+str(timeDifference)
		channelSelectONE = channelSelectTWO

		channelsPicked = []
		channelSelect = randint(0, totalChannels-1)
		channelsPicked.append(channelSelect)

		print str(activeChannels)+" channels active."
		dataset = mongo.snippetPicker(topic, mode)
		durationChannelONE = snippetProcessing(topic, dataset, channelSelect, True)
		print "writing snippet on channel "+str(channelSelect+1)+"."


		for channel in range(1, activeChannels):
			newChannelSelect = randint(0, totalChannels-1)
			while (newChannelSelect in channelsPicked):
				newChannelSelect = randint(0, totalChannels-1)
			channelsPicked.append(newChannelSelect)
			durationONE = str(durationChannelONE)
			dataset = mongo.snippetFill(topic, durationONE)
			if dataset is not None:
				durationFill = snippetProcessing(topic, dataset, channel, True)
				blackDuration = durationChannelONE - durationFill
				if (blackDuration != 0):
					blacksAdder(blacks, blackDuration, channel)
				else:
					print "no black fills needed."
			else:
				print "not enough snippets for snippetFill."

		for emptyChannel in range(0, totalChannels):
				if (emptyChannel not in channelsPicked):
					blacksAdder(blacks, durationChannelONE, emptyChannel)

		totalTime += durationChannelONE
		breaksToAll(breaks, breakDuration)	

def modeFOUR(topic, phaseLength, activeChannels, mode, breaks, blacks):
	print "----> entering modeFOUR."
	global totalTime
	global durationChannelONE
	global channelSelectONE, channelSelectTWO
	global diffenceBlack
	global roundCounter
	
	oldTopic = (activeChannels / 2)
	newTopic = activeChannels - oldTopic

	timeDifference = phaseLength - totalTime

	while (totalTime < phaseLength):
		print "totalTime: "+str(totalTime)
		print "phaseLength: "+str(phaseLength)
		print "timeDifference: "+str(timeDifference)
		channelSelectONE = channelSelectTWO

		channelSelect = randint(0, activeChannels-1)
		channelsPicked = []
		channelsPicked.append(channelSelect)

		print str(oldTopic)+" channels active for current topic."
		dataset = mongo.snippetPicker(topic, mode)
		durationChannelONE = snippetProcessing(topic, dataset, channelSelect, True)
		print "writing snippet on channel "+str(channelSelect+1)+"."

		if (activeChannels != 1):
			print "\nadding channels with current topic content."
			for channel in range(oldTopic-1):
				newChannelSelect = randint(0, totalChannels-1)
				while (newChannelSelect in channelsPicked):
					newChannelSelect = randint(0, totalChannels-1)
				channelsPicked.append(newChannelSelect)
				durationONE = str(durationChannelONE)
				dataset = mongo.snippetFill(topic, durationONE)
				if dataset is not None:
					durationFill = mongo.snippetProcessing(topic, dataset, channel, True)
					blackDuration = durationChannelONE - durationFill
					if (blackDuration != 0):
						blacksAdder(blacks, blackDuration, channel)
					else:
						print "no black fills needed."
				else:
					print "not enough snippets for snippetFill."

			print "\nadding channels with next topic content."
			for channel in range(newTopic-1):
				newChannelSelect = randint(0, totalChannels-1)
				while (newChannelSelect in channelsPicked):
					newChannelSelect = randint(0, totalChannels-1)
				channelsPicked.append(newChannelSelect)
				nextONE = nextTopic[roundCounter]
				dataset = mongo.snippetFill(nextONE, durationONE)
				if dataset is not None:
					durationFill = mongo.snippetProcessing(nextONE, dataset, channel, True)
					blackDuration = durationChannelONE - durationFill
					if (blackDuration != 0):
						blacksAdder(blacks, blackDuration, channel)
					else:
						print "no black fills needed."
				else:
					print "not enough snippets for snippetFill."

		for emptyChannel in range(0, totalChannels-1):
				if (emptyChannel not in channelsPicked):
					blacksAdder(blacks, durationChannelONE, emptyChannel)

		breaksToAll(breaks, breakDuration)					


def snippetProcessing(topic, dataset, channelSelect, buffer):
	global totalTime
	filename = dataset['filename']
	duration = dataset['duration']
	duration = int(duration)
	#mongo.pickUpdateFilename(filename)
	print filename
	content = "file '/Users/MH/Projects/Youtube-Crawler/exports/snippets/"+topic+"/"+filename+"'\n"
	thisfile = "/Users/MH/Projects/Youtube-Crawler/exports/batchfiles/"+exportfiles[channelSelect]
	channelFileOne = open(thisfile, 'a')
	channelFileOne.write(content)
	channelFileOne.close()
	if (buffer == True):
		return duration



def breaksToAll(breaks, breakDuration):
	global totalTime
	if breaks == True:
		totalTime += breakDuration
		print "adding "+str(breakDuration)+" second breaks on all channels."
		for channel in otherChannels:
			for second in range(0, breakDuration):
				content = "file '/Users/MH/Projects/Youtube-Crawler/exports/black/black_720.mp4'\n"
				thisfile = "/Users/MH/Projects/Youtube-Crawler/exports/batchfiles/"+exportfiles[channel]
				channelFileOther = open(thisfile, 'a')
				channelFileOther.write(content)
				channelFileOther.close()
	else:
		print "skipping breaks."


def blacksAdder(blacks, blackDuration, channelSelect):
	if blacks == True:
		print "adding black for channel "+str(channelSelect+1)+" with the length of "+str(blackDuration)+"."
		for second in range(0, blackDuration):
			content = "file '/Users/MH/Projects/Youtube-Crawler/exports/black/black_720.mp4'\n"
			thisfile = "/Users/MH/Projects/Youtube-Crawler/exports/batchfiles/"+exportfiles[channelSelect]
			channelFileOne = open(thisfile, 'a')
			channelFileOne.write(content)
			channelFileOne.close()
	else:
		print "skipping blacks."		
			


def makeVideo():
	for filename in exportfiles:
		name = filename.split(".")[0]
		commandline = "./ffmpeg -f concat -i /Users/MH/Projects/Youtube-Crawler/exports/batchfiles/"+filename+"  -c copy -r 25.0 /Users/MH/Projects/Youtube-Crawler/exports/output/"+name+".mp4"
		snippet = shlex.split(commandline)
		subprocess.Popen(snippet)
		print "exporting "+ name + " done."
	print "all videofiles written, quitting program.\nBye bye."


if __name__ == '__main__':
	#mongo
	mongo.init()
	mongo.dropAndReconnect()

	#cleanup and load
	clearExportfiles()
	
	if (totalChannels >= 4):
		channelSetup(totalChannels)
		loadSnippetsToDb()
	
		#write new files
		makeFiles()
	
		#cleanup and write new videos
		clearOutputfiles()
		makeVideo()
	else:
		print "totalChannels is to low, 4 channels are minimum."



