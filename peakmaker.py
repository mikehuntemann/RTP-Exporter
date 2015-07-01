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
nextTopic = ["ebola", "germanwings"]
exportfiles = ["channelFileONE.txt", "channelFileTWO.txt", "channelFileTHREE.txt", "channelFileFOUR.txt"]
importCollection =  {"ebola", "germanwings"}
collection = {"ebola"}
#"NSA", "mh370", "ebola", "charlie", "germanwings"

#total loop length in seconds
totalTime = 0

#individual Times (!used)
ChannelONETime = 0
ChannelTWOTime = 0
ChannelTHREETime = 0
ChannelFOURTime = 0
channelONEdone = False
channelTWOdone = False
channelTHREEdone = False
channelFOURdone = False
durationChannelONE = 0

#Multichannel settings
channelSelectONE = 0
channelSelectTWO = 0

#default settings
breakDuration = 1
activeChannel = 1
totalChannels = 4
otherChannels = [0, 1, 2, 3]
blacks = True
breaks = True
def clearExportfiles():
	for filename in os.listdir("exports/batchfiles/"):
			if filename.endswith(".txt"):
				print filename +" found."
				os.remove("exports/batchfiles/"+filename)
				print filename + " removed."

def clearOutputfiles():
	for filename in os.listdir("exports/output/"):
			if filename.endswith(".mp4"):
				print filename +" found."
				os.remove("exports/output/"+filename)
				print filename + " removed."


def loadSnippetsToDb():
	for topic in importCollection:
		print "\nworking in "+topic+" directory.\n"
		for filename in os.listdir("exports/snippets/"+topic+"/"):
			if filename.endswith(".mp4"):
				#print filename
				# filename structure: 0AnzzuOuw4w_00/00/39-5.mp4
				tinyurl = re.findall("\w{11}", filename)[0]
				#print tinyurl
				#[-1:] = last char in a string
				duration = filename.split(".")[0][-1:]
				#print duration
				try:
					mongo.saveSnippet(topic, filename, duration, tinyurl)
				except:
					pass
				#print tinyurl + " added -> mongodb with the duration of "+duration+".\n"
			else:
				print "file is no .mp4 file."
	print "done adding content to mongodb. \n"

#phase 1: 1 Channel, 3 sek breaks, > 5 sec clips. [30 sec]
#phase 2: 2 Channels, 3 sek breaks, > 5 sec clips. [30 sec]
#phase 3: 4 Channels, no breaks, 1-3 sec clips only. [1 min]
#phase 4: 3 Channels [2-1 Topics], 3 sec breaks, > 5 sec clips [30 sec]
#phase 5: 2 Channels [1-1 Topics], 3 sec breaks, > 5 sec clips [30 sec]
#phase 6: phase 2.
#repeat.
def makeFiles():
	for topic in collection:
		print "working on topic: "+topic+"." 
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		# if topic is firsttopic do phase 1
		#phase 1:
		makePhase(topic, phaseLength = 30, activeChannels =  1, mode = 2, breaks = False, blacks = True)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		#phase 2:
		makePhase(topic, phaseLength = totalTime + 60, activeChannels = 2, mode = 2, breaks = False, blacks = True)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		#phase 3:
		makePhase(topic, phaseLength = totalTime + 30, activeChannels = 4, mode = 1, breaks = False, blacks = False)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		#phase 4:
		makePhase(topic, phaseLength = totalTime + 30, activeChannels = 3, mode = 3, breaks = True, blacks = True)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		#phase 5:
		makePhase(topic, phaseLength = totalTime + 60, activeChannels = 2, mode = 3, breaks = True, blacks = True)
		print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
		#restarting
		#switching nextTopic +1
		#if last topic phase 2 in the end instead of phase 5
	
	print "Total project length is "+ str(totalTime)+" seconds."
	print "file done."

def makePhase(topic, phaseLength, activeChannels, mode, breaks, blacks):
	global totalTime, ChannelONETime, ChannelTWOTime, ChannelTHREETime, ChannelFOURTime
	global channelONEdone, channelTWOdone, channelTHREEdone, channelFOURdone
	global durationChannelONE
	global channelSelectONE, channelSelectTWO
	global diffenceBlack
	global nextTopic

	print "starting on making a phase."
	while (totalTime < phaseLength):
		timeDifference = phaseLength - totalTime
		print "totalTime: "+str(totalTime)
		print "phaseLength: "+str(phaseLength)
		print "timeDifference: "+str(timeDifference)
		channelSelectONE = channelSelectTWO
		
		if (mode == 3):
			if (activeChannels == 3):
				print "three channels active."
				availableChannels = []
				channelSelect = randint(0, totalChannels-1)
				print "channel "+str(channelSelect+1)+" is going to be ignored."
				for channel in otherChannels:
					if (channel != channelSelect):
						availableChannels.append(channel)
				print availableChannels
				
				#mode = snippets which are 6 seconds and below.
				print "processing first snippet."
				dataset1 = mongo.snippetPicker(topic, mode)
				firstLane = availableChannels[0]
				print "channel "+str(firstLane+1)+" for first snippet."
				durationChannelONE = snippetProcessing(topic, dataset1, firstLane, buffer = True)
				
				#same topic, same length
				print "processing second snippet."
				dataset2 = mongo.snippetFitter(topic, str(durationChannelONE))
				secondLane = availableChannels[1]
				print "channel "+str(secondLane+1)+" for second snippet."
				print "topic is: "+str(topic)
				snippetProcessing(topic = topic, dataset = dataset2, channelSelect = secondLane, buffer = False)
	
				#next topic, same length
				print "processing third snippet."
				nextONE = nextTopic[1]
				print "topic is: "+str(nextONE)
				thirdLane = availableChannels[2]
				print "channel "+str(thirdLane+1)+" for third snippet."
				dataset3 = mongo.snippetFitter(nextONE, str(durationChannelONE))
				snippetProcessing(topic = nextONE, dataset = dataset3, channelSelect = thirdLane, buffer = False)
				blacksAdder(blacks, durationChannelONE, channelSelect)
				breaksToAll(breaks, breakDuration)
				totalTime += durationChannelONE
			
			if (activeChannels == 2):
				print "two channels active."
				dataset1 = mongo.snippetPicker(topic, mode)
				nextONE = nextTopic[1]
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



		if (mode == 2):
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

			if (activeChannels == 2):
				print "two channels active."
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

		if (mode == 1):
			
			print "entering mode 1. \n"
			print "totalTime is:"
			print totalTime
			print "phaseLength:"
			print phaseLength
			maxDuration = phaseLength-totalTime-3
			print "PEAKduration is: "+str(phaseLength-totalTime)

			#CHANNEL 1
			while (channelONEdone == False):
				print "\nentering channelONE..."
				print "ChannelONETime is: "+str(ChannelONETime)
				durationDifference = (phaseLength - totalTime) - ChannelONETime
				print "durationDifference is "+str(durationDifference)
				if (durationDifference >= 3):
					dataset1 = mongo.snippetPicker(topic, mode)
					if dataset1 is not None:
						durationChannelONE = snippetProcessing(topic, dataset1, 0, True)
						ChannelONETime += durationChannelONE
					else:
						print "no more snippets in mongodb."
				else:
					if (durationDifference != 0):
						durationDifference = str(durationDifference)
						print "preparing last snippets for channel 1"
						dataset1 = mongo.snippetFitter(topic, durationDifference)
						if dataset1 is not None:
							snippetProcessing(topic, dataset1, 0, False)
							print "added fitting snipped\ndone with channelONE."
							print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
							channelONEdone = True
						else:
							print "couldn't find a fitting snippet for channel 1."
					else:
						print "already fitting\ndone with channelONE."
						print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
						channelONEdone = True

			#CHANNEL 2
			while (channelTWOdone == False):
				print "\nentering channelTWO..."
				print "ChannelTWOTime is: "+str(ChannelTWOTime)
				durationDifference = (phaseLength - totalTime) - ChannelTWOTime
				print "durationDifference is "+str(durationDifference)
				if (durationDifference >= 3):
					dataset2 = mongo.snippetPicker(topic, mode)
					if dataset2 is not None:
						durationChannelTWO = snippetProcessing(topic, dataset2, 1, True)
						ChannelTWOTime += durationChannelTWO
					else:
						print "no more snippets in mongodb."
				else:
					if (durationDifference != 0):
						durationDifference = str(durationDifference)
						print "preparing last snippets for channel 2"
						dataset2 = mongo.snippetFitter(topic, durationDifference)
						if dataset2 is not None:
							snippetProcessing(topic, dataset2, 1, False)
							print "added fitting snipped\ndone with channelTWO."
							print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
							channelTWOdone = True
						else:
							print "couldn't find a fitting snippet for channel 2."
					else:
						print "already fitting\ndone with channelTWO."
						print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
						channelTWOdone = True


			#CHANNEL 3
			while (channelTHREEdone == False):
				print "\nentering channelTHREE..."
				print "ChannelTHREETime is: "+str(ChannelTHREETime)
				durationDifference = (phaseLength - totalTime) - ChannelTHREETime
				print "durationDifference is "+str(durationDifference)
				if (durationDifference >= 3):
					dataset3 = mongo.snippetPicker(topic, mode)
					if dataset3 is not None:
						durationChannelTHREE = snippetProcessing(topic, dataset3, 2, True)
						ChannelTHREETime += durationChannelTHREE
					else:
						print "no more snippets in mongodb."
				else:
					if (durationDifference != 0):
						durationDifference = str(durationDifference)
						print "preparing last snippets for channel 2"
						dataset3 = mongo.snippetFitter(topic, durationDifference)
						if dataset3 is not None:
							snippetProcessing(topic, dataset3, 2, False)
							print "added fitting snipped\ndone with channelTHREE."
							print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
							channelTHREEdone = True
						else:
							print "couldn't find a fitting snippet for channel 3."
					else:
						print "already fitting\ndone with channelTHREE."
						print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
						channelTHREEdone = True

			#CHANNEL 3
			while (channelFOURdone == False):
				print "\nentering channelFOUR..."
				print "ChannelFOURTime is: "+str(ChannelFOURTime)
				durationDifference = (phaseLength - totalTime) - ChannelFOURTime
				print "durationDifference is "+str(durationDifference)
				if (durationDifference >= 3):
					dataset4 = mongo.snippetPicker(topic, mode)
					if dataset4 is not None:
						durationChannelFOUR = snippetProcessing(topic, dataset4, 3, True)
						ChannelFOURTime += durationChannelFOUR
					else:
						print "no more snippets in mongodb."
				else:
					if (durationDifference != 0):
						durationDifference = str(durationDifference)
						print "preparing last snippets for channel 2"
						dataset4 = mongo.snippetFitter(topic, durationDifference)
						if dataset4 is not None:
							snippetProcessing(topic, dataset4, 3, False)
							print "added fitting snipped\ndone with channelFOUR."
							print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
							channelFOURdone = True
						else:
							print "couldn't find a fitting snippet for channel 4."
					else:
						print "already fitting\ndone with channelFOUR."
						print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n"
						channelFOURdone = True
			
			if (channelONEdone == True and channelTWOdone == True and channelTHREEdone == True and channelFOURdone == True):
				print "all channels are done with peak sequence."
				totalTime += timeDifference

	print "phase finished."


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
	loadSnippetsToDb()
	
	#cleanup and write new files
	clearExportfiles()
	makeFiles()
	
	#cleanup and write new videos
	clearOutputfiles()
	makeVideo()



