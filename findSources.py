import os, sys

collection = []

def findSources():
	for filename in os.listdir("test/"):
		filename = str(filename)
		collection.append(filename)
	for item in collection:
		print item
if __name__ == '__main__':
	findSources()