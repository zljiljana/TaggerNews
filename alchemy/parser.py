#!/usr/bin/python

from urllib2 import Request, urlopen
import requests
import tags
import string
import rethinkdb as r
import json
import os
from firebase import firebase

firebase = firebase.FirebaseApplication('https://hacker-news.firebaseio.com', authentication = None)

RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015

connection = r.connect(host=RDB_HOST, port=RDB_PORT)

def getPageInfo():
	myURL = 'https://news.ycombinator.com'
	response = urlopen(Request(myURL))
	return response

def openHtml(response):
	dir = os.path.dirname(__file__)
	path = os.path.join(dir, '../app/templates/hn_tag.html')
	f = open(path, "w")
	add = "<html op=\"news\"><head><meta name=\"referrer\" content=\"origin\"><link rel=\"stylesheet\" type=\"text/css\" href=\"news.css?EfSg70JZhNeQ93ByKLi6\"><link rel=\"shortcut icon\" href=\"favicon.ico\"><link rel=\"alternate\" type=\"application/rss+xml\" title=\"RSS\" href=\"rss\">"
	f.write(add)
	add = "<link href=\"../static/css/news.css\" rel=\"stylesheet\"><script type=\"text/javascript\">function hide(id) {var el = document.getElementById(id); if (el) { el.style.visibility = 'hidden'; }} function vote(node) {var v = node.id.split(/_/);var item = v[1];hide('up_'   + item);hide('down_' + item);var ping = new Image();ping.src = node.href;return false;}"
	f.write(add)
	add = "</script><title>Tagger News</title></head><body><center><table id=\"hnmain\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" width=\"85%\" bgcolor=\"#f6f6ef\"><tr><td bgcolor=\"#ff6600\"><table border=\"0\" cellpadding=\"0\" cellspacing=\"0\" width=\"100%\" style=\"padding:2px\"><tr><td style=\"width:18px;padding-right:4px\"><a href=\"http://www.ycombinator.com\"><img src=\"../static/y18.gif\" width=\"18\" height=\"18\" style=\"border:1px #ffffff solid;\"></a></td><td style=\"line-height:12pt; height:10px;\"><span class=\"pagetop\"><b><a href=\"/input\">Tagger News</a></b><img src=\"../static/s.gif\" height=\"1\" width=\"10\"><a href=\"https://github.com/zljiljana/TaggerNews\">github</a> | <a href=\"https://github.com/zljiljana/TaggerNews\">slides</a></span></td><td style=\"text-align:right;padding-right:4px;\"><span class=\"pagetop\"><a href=\"mailto:zigicljiljana@gmail.com\">zigicljiljana@gmail.com</a></span></td>"
	f.write(add)
	add = "</tr></table> <tr style=\"height:10px\"></tr><tr style=\"height:10px\"></tr><tr><td>"
	f.write(add)
	add = "<div class=\"container\"><div class = \"container\"><form  action=\"/filter\" method=\"GET\"><div class=\"form-group\"><input type=\"text\" id=\"ID\" name='ID' placeholder=\"e.g. data science\"><button type=\"submit\" class=\"btn btn-default btn-lg\">Filter!</button></div></form></div><script src=\"https://code.jquery.com/jquery-1.10.2.min.js\"></script><script src=\"static/js/bootstrap.min.js\"></script></div>"
	f.write(add)
	return f

def parse():
	response = getPageInfo()
	f = openHtml(response)
	i = 0
	while (i<23):
		p = response.readline()
		i+=1
	i = 0
	while (p):
		p = response.readline()
		itemid = getItemID(p)
		if (itemid != 0):
			# check if the itemID is in the rethinkDB, if it is then return the to_insert string
			to_insert = getTags(itemid)
		index = p.rfind("<span class=\"deadmark\"></span>")
		if index != -1:
			if p.find("sitebit comhead") != -1:
				index += p[index:].rfind("</a>")+5+7 # add offset
			else:
				index += p[index:].rfind("</a>")+4
			if (itemid == 0):
				to_insert = "<td><div class=\"boxed\">url-error</div></td>"
			p_tmp = p[:index] + to_insert + p[index:]
			p = p_tmp
			i+=1
		f.write(p)
	f.close() 
	print "Main page tags set."
	# check if 300-popular dictionary already has the data
	if (r.db('test').table('tag_dict').count().run(connection) == 0):
		setDictionary()
	print "Dictionary ready."


def getTags(itemid):
	res = list(r.db("test").table("itemid_dict").filter({'id': itemid}).run(connection))
	if res==[]:
		(to_insert, tags) = selectTags(itemid)
		r.db("test").table("itemid_dict").insert({ "id": itemid, "tag_string": to_insert}).run(connection)
		return to_insert
	else:
		# data is in the rethinkDB
		to_insert = res[0]['tag_string']
		return str(to_insert)



def getItemID(html_row):
	itemid = 0
	pos1 = html_row.find("id=\"up_")
	pos2 = html_row.find("tem?id=")
	if ((pos1 != -1) or (pos2 != -1)):
		position = max(pos1, pos2)
		itemid = html_row[position+7:position+7+8]
	return itemid


def selectTags(itemid):
	try:
		data = firebase.get('/v0/item/' + str(itemid), None)
		url = data['url']
	except KeyError:
		url = data['type']
		if url == ('job' or 'pollopt' or 'poll' or 'comment'):
			to_insert = "<td><div class=\"boxed\">" + url +"</div></td>"
			tagses = [url]
			return (to_insert, tagses)
		else:
			to_insert = "<td><div class=\"boxed\">url-error</div></td>"
			tagses = ['url-error']
			return (to_insert, tagses)



	topKW = tags.getKeywords(url)
	if len(topKW) > 2:
		t = tags.getTags(topKW)
		t0 = ' '.join(t[0].split('_'))
		t1 = ' '.join(t[1].split('_'))
		tagses = [t0, t1]
		if topKW[0] in tagses:
			t2 = topKW[1]
			t3 = topKW[2]
			# if len(topKW) > 3:
			# 	if topKW[1] in tagses:
			# 		t2 = topKW[2]
			# 		t3 = topKW[3]				
		else:
			t2 = topKW[0]
			t3 = topKW[1]
		to_insert = "<td><div class=\"boxed\">" + t0+" | "+t1+" | "+t2+" | "+t3+"</div></td>"
	else:
		try: 
			to_insert = "<td><div class=\"boxed\">" + topKW[0] +"</div></td>"
			tagses = topKW
		except IndexError:
			to_insert = "<td><div class=\"boxed\">keywords-not-found</div></td>"
			tagses = ['keywords-not-found']

	filtered = filter(lambda x: x in string.printable, to_insert)
	return (filtered, tagses)


def add(key, value, dict):
	try:
		if (dict[key]): # if it exists just update the list
			dict[key] += [value]
	except KeyError:
		dict[key] = [value]


def setDictionary():
	dict = {}
	#print "getting top stories from hacker-news"
	result = firebase.get('/v0/topstories', None)
	# result = result[:200]
	for itemid in result:
		try:
			data = firebase.get('/v0/item/' + str(itemid), None)
			if (data['type'] == 'story'):
				# get tags
				url = data['url']
				(to_insert, tags) = selectTags(itemid)
				# store to temp db
				r.db("test").table("itemid_dict").insert({"id": itemid, "tag_string": to_insert}).run(connection)
				if len(tags) > 1:
					title = data['title']
					score = str(data['score'])
					usr = data['by']
					comments = str(data['descendants'])
					myString = "<tr class='athing'><td align=\"right\" valign=\"top\" class=\"title\"><span class=\"rank\"> </span></td><td><center><a id=\"up_10287983\"><div class=\"votearrow\" title=\"upvote\"></div></a></center></td><td class=\"title\"><span class=\"deadmark\"></span><a href=\"" + url + "\">" + title + "</a>" + to_insert + "</td><td><center><a id=\"up_10287983\"><div class=\"votearrow\" title=\"upvote\"></div></a></center></td></tr><tr><td colspan=\"2\"></td><td class=\"subtext\"><span class=\"score\">" + score + " points</span> by <a>" + usr + "</a> | <a>" + comments +" comments</a></td></tr><tr class=\"spacer\" style=\"height:5px\"></tr>"
					print "tags: ", tags[0], tags[1]
					add(tags[0], myString, dict)
					add(tags[1], myString, dict)
		except KeyError:
			pass
	# r.db("test").table("tag_dict").delete().run(connection)
	r.db("test").table("tag_dict").insert(dict).run(connection)
