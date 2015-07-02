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
totalChannels = 6

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
	#ungerade olus 1 alle zeit zahlen
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
	 	screenExtender2 = 0
	 	print "screenExtender1.4: "+str(screenExtender1)

	#plus 1 ab 6
	if (totalChannels > 5):
	 	times = totalChannels - 5
	 	screenExtender3 = times
	 	print "screenExtender2: "+str(screenExtender3)
	else:
	 	screenExtender3 = 0
	 	print "screenExtender2: "+str(screenExtender3)


def clearExportfiles():
	for filename in os.listdir("/Users/MH/Projects/Youtube-Crawler/exports/batchfiles/"):
			if filename.endswith(".txt"):
				print filename +" found."
				os.remove("/Users/MH/Projects/Youtube-Crawler/exports/batchfiles/"+filename)
				print filename + " removed."


def clearOutputfiles():
	for filename in os.listdir("exports/output/"):
			if filename.endswith(".mp4"):
				print filename +" found."
				os.remove("exports/output/"+filename)
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


def makeFiles(screenExtender1, screenExtender2, screenExtender3):
	global roundCounter
	
	#phase 1: 1 Channel, 3 sek breaks, > 5 sec clips. [30 sec]
	#phase 2: 2 Channels, 3 sek breaks, > 5 sec clips. [30 sec]
	#phase 3: 4 Channels, no breaks, 1-3 sec clips only. [1 min]
	#phase 4: 3 Channels [2-1 Topics], 3 sec breaks, > 5 sec clips [30 sec]
	#phase 5: 2 Channels [1-1 Topics], 3 sec breaks, > 5 sec clips [30 sec]
	#phase 6: phase 2.
	#repeat.
	
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
	#switching topic
	#restarting
	#if last topic phase 2 in the end instead of phase 5
	
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
	

	print "entering mode 1. \n"
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
	# -----> make it variable with activeChannels!

	global totalTime
	global durationChannelONE
	global channelSelectONE, channelSelectTWO
	global diffenceBlack
	global nextTopic, roundCounter
	timeDifference = phaseLength - totalTime

	while (totalTime < phaseLength):
		print "totalTime: "+str(totalTime)
		print "phaseLength: "+str(phaseLength)
		print "timeDifference: "+str(timeDifference)
		print "roundCounter: "+str(roundCounter)
		channelSelectONE = channelSelectTWO
	
		if (activeChannels == 3):
			print "three channels active."
			availableChannels = []
			if (totalChannels == 4):
				channelSelectONE = randint(0, totalChannels-1)
				print "channel "+str(channelSelectONE+1)+" is going to be ignored."
				for channel in otherChannels:
					if (channel != channelSelectONE):
						availableChannels.append(channel)
			else:
				while (channelSelectONE == channelSelectTWO):
					channelSelectONE = randint(0, totalChannels-1)
					channelSelectTWO = randint(0, totalChannels-1)
				print "channel "+str(channelSelectONE+1)+" and "+str(channelSelectTWO+1)+" are going to be ignored."
				for channel in otherChannels:
					if (channel != channelSelectONE):
						if (channel != channelSelectTWO):
							availableChannels.append(channel)
			print availableChannels
			
			#mode = snippets which are 6 seconds and below.
			print "\nprocessing first snippet."
			dataset1 = mongo.snippetPicker(topic, mode)
			firstLane = availableChannels[0]
			print "channel "+str(firstLane+1)+" for first snippet."
			durationChannelONE = snippetProcessing(topic, dataset1, firstLane, buffer = True)
			
			#same topic, same length
			print "\nprocessing second snippet."
			dataset2 = mongo.snippetFitter(topic, str(durationChannelONE))
			secondLane = availableChannels[1]
			print "channel "+str(secondLane+1)+" for second snippet."
			print "topic is: "+str(topic)
			snippetProcessing(topic = topic, dataset = dataset2, channelSelect = secondLane, buffer = False)

			#next topic, same length
			print "\nprocessing third snippet."
			nextONE = nextTopic[roundCounter]
			print "topic is: "+str(nextONE)
			thirdLane = availableChannels[2]
			print "channel "+str(thirdLane+1)+" for third snippet."
			dataset3 = mongo.snippetFitter(nextONE, str(durationChannelONE))
			snippetProcessing(topic = nextONE, dataset = dataset3, channelSelect = thirdLane, buffer = False)
			print ""
			if (totalChannels == 4):
				blacksAdder(blacks, durationChannelONE, channelSelectONE)
			else:
				blacksAdder(blacks, durationChannelONE, channelSelectONE)
				blacksAdder(blacks, durationChannelONE, channelSelectTWO)
			print ""
			breaksToAll(breaks, breakDuration)
			totalTime += durationChannelONE
			print "\n--------------------------"
		
		if (activeChannels == 2):
			print "two channels active."
			dataset1 = mongo.snippetPicker(topic, mode)
			nextONE = nextTopic[roundCounter]
			dataset2 = mongo.snippetPicker(nextONE, mode)
			#random select 2 different channels with different content
			while (channelSelectONE == channelSelectTWO):
				channelSelectONE = randint(0, totalChannels-1)
				channelSelectTWO = randint(0, totalChannels-1)
			print "writing first snippet on channel "+str(channelSelectONE+1)+"."
			print "writing second snippet on channel "+str(channelSelectTWO+1)+"."
			#for each channel grab a snippet (!problem: different length but need the same length when adding blacks!)
			durationChannelONE = snippetProcessing(topic, dataset1, channelSelectONE, True)
			print "durationChannelONE is: "+str(durationChannelONE)
			durationChannelTWO = snippetProcessing(nextONE, dataset2, channelSelectTWO, True)
			print "durationChannelTWO is: "+str(durationChannelTWO)
			#duration comparison, then adding the difference to the shorter snippet, adding the bigger duration as black to empty channels
			if (durationChannelONE != durationChannelTWO):
				if (durationChannelONE > durationChannelTWO):
					diffenceBlack = durationChannelONE - durationChannelTWO
					print "channelONE is "+str(diffenceBlack)+" seconds longer than channelTWO."
					blacksAdder(True, diffenceBlack, channelSelectTWO)
					totalTime += durationChannelONE
					for channel in otherChannels:
						if (channel != channelSelectONE):
							if (channel != channelSelectTWO):
								blacksAdder(blacks, durationChannelONE, channel)
							else:
								print "channel "+str(channel+1)+" is skipped."
						else:
							print "channel "+str(channel+1)+" is skipped."
				else:
					diffenceBlack = durationChannelTWO - durationChannelONE
					print "channelTWO is "+str(diffenceBlack)+" seconds longer than channelONE."
					print "adding "+str(diffenceBlack)+" seconds to channelONE."
					blacksAdder(True, diffenceBlack, channelSelectONE)
					totalTime += durationChannelTWO
					for channel in otherChannels:
						if (channel != channelSelectONE):
							if (channel != channelSelectTWO):
								blacksAdder(blacks, durationChannelTWO, channel)
							else:
								print "channel "+str(channel+1)+" is skipped."
						else:
							print "channel "+str(channel+1)+" is skipped."
			#duration is equal, just filling the empty channels with black
			else:
				print "duration of both channels are equal."
				totalTime += durationChannelONE
				for channel in otherChannels:
					if (channel != channelSelectONE):
						if (channel != channelSelectTWO):
							blacksAdder(blacks, durationChannelONE, channel)
			breaksToAll(breaks, breakDuration)


def modeONE(topic, phaseLength, activeChannels, mode, breaks, blacks):
	# -----> make it variable with activeChannels!

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

		if (activeChannels == 1):
			print "one channel active."
			dataset = mongo.snippetPicker(topic, mode)
			#random channel 0 to 3 in otherChannel to select .txt file
			channelSelect = randint(0, totalChannels-1)
			print "writing snippet on channel "+str(channelSelect+1)+"."
			blackDuration = snippetProcessing(topic, dataset, channelSelect, True)
			totalTime += blackDuration
			for channel in otherChannels:
				if (channel != channelSelect):
					blacksAdder(blacks, blackDuration, channel)
				else:
					print "channel "+str(channel+1)+" was skipped."
			breaksToAll(breaks, breakDuration)
			print ""
		
		if (activeChannels == 2):
			print "two channels active.\n"
			dataset1 = mongo.snippetPicker(topic, mode)
			dataset2 = mongo.snippetPicker(topic, mode)
			#random select 2 different channels with different content
			while (channelSelectONE == channelSelectTWO):
				channelSelectONE = randint(0, totalChannels-1)
				channelSelectTWO = randint(0, totalChannels-1)
			print "writing first snippet on channel "+str(channelSelectONE+1)+"."
			print "writing second snippet on channel "+str(channelSelectTWO+1)+"."
			#for each channel grab a snippet (!problem: different length but need the same length when adding blacks!)
			durationChannelONE = snippetProcessing(topic, dataset1, channelSelectONE, True)
			print "durationChannelONE is: "+str(durationChannelONE)
			durationChannelTWO = snippetProcessing(topic, dataset2, channelSelectTWO, True)
			print "durationChannelTWO is: "+str(durationChannelTWO)
			#duration comparison, then adding the difference to the shorter snippet, adding the bigger duration as black to empty channels
			if (durationChannelONE != durationChannelTWO):
				if (durationChannelONE > durationChannelTWO):
					diffenceBlack = durationChannelONE - durationChannelTWO
					print "channelONE is "+str(diffenceBlack)+" seconds longer than channelTWO."
					blacksAdder(True, diffenceBlack, channelSelectTWO)
					totalTime += durationChannelONE
					for channel in otherChannels:
						if (channel != channelSelectONE):
							if (channel != channelSelectTWO):
								blacksAdder(blacks, durationChannelONE, channel)
							else:
								print "channel "+str(channel+1)+" is skipped."
						else:
							print "channel "+str(channel+1)+" is skipped."
				else:
					diffenceBlack = durationChannelTWO - durationChannelONE
					print "channelTWO is "+str(diffenceBlack)+" seconds longer than channelONE."
					print "adding "+str(diffenceBlack)+" seconds to channelONE."
					blacksAdder(True, diffenceBlack, channelSelectONE)
					totalTime += durationChannelTWO
					for channel in otherChannels:
						if (channel != channelSelectONE):
							if (channel != channelSelectTWO):
								blacksAdder(blacks, durationChannelTWO, channel)
							else:
								print "channel "+str(channel+1)+" is skipped."
						else:
							print "channel "+str(channel+1)+" is skipped."
			#duration is equal, just filling the empty channels with black
			else:
				print "duration of both channels are equal."
				totalTime += durationChannelONE
				for channel in otherChannels:
					if (channel != channelSelectONE):
						if (channel != channelSelectTWO):
							blacksAdder(blacks, durationChannelONE, channel)
			breaksToAll(breaks, breakDuration)
			print ""

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
	#mongo.init()
	#mongo.dropAndReconnect()

	#cleanup and load
	#clearExportfiles()
	
	if (totalChannels >= 4):
		channelSetup(totalChannels)
		#loadSnippetsToDb()
	
		#write new files
		#makeFiles()
	
		#cleanup and write new videos
		#clearOutputfiles()
		#makeVideo()
	else:
		print "totalChannels is to low, 4 channels are minimum."



