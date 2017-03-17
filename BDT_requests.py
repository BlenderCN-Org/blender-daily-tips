# -----------------------------------------------------------------------------
# Blender Tips - Addon for daily blender tips
# Developed by Patrick W. Crawford
#

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import bpy
import threading
import urllib.request
import urllib
import json
import sys, os # for error handling

from . import conf
from . import BDT_ui


# -----------------------------------------------------------------------------
# Requests
# -----------------------------------------------------------------------------



def bdt_fetch_tips():
	"""Function that generates all requests, runs in async"""

	# context even needed?

	# first, get the list of subscribed tips from preferences
	addon_prefs = bpy.context.user_preferences.addons[__package__].preferences

	tips = []

	# Each subscription tip type has the format:
	# {"title":title,"description":desc,"date":date,"thumb":tmb_path}

	# consider doing threads even for each of these linear-requests
	if addon_prefs.tips_blendernation==True:
		# also wrap in a try/catch
		res,e = fetch_blendernation()
		if res!=None:
			tips.append(res)
		if e!=None:
			# some kind of error occured
			print("BDT - Error on fetching blendernation: ",str(e))
	
	if addon_prefs.tips_yanal_sosak==True:
		# also wrap in a try/catch
		res,e = fetch_yanal_sosak()
		if res!=None:
			tips.append(res)
		if e!=None:
			# some kind of error occured
			print("BDT - Error on fetching Yanal Sosak: ",str(e))

	print("Finished gathering tips: ")
	print(tips)

	## call function for adding to handler??? in ui code



def fetch_blendernation():
	# source to parse:
	# https://www.blendernation.com/category/education/
	return None,"Not implemented yet"


def fetch_yanal_sosak():

	#return None,"Not implemented yet"

	# Static playlsit URL for this source
	yt_playlist_id = "PLvPwLecDlWRCaTVFs7Tx_1Mz8EDd0S8_5"

	# Used to run commands
	yt_data3_key = fetch_yt_devkey()

	yt_playlist_contents = []
	countout = 0
	nextPageToken = "" # for getting subsequent pages
	yt_playbase = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId="

	# loop through all pages of playlsit, chopped into sets of 50-videos per page
	while countout<25:
		countout +=1
		yt_playlist_url = "{}{}{}&key={}".format(
				yt_playbase,yt_playlist_id,nextPageToken,yt_data3_key)		
		print("Requesitng playlist pg{}, url: {}".format(
				countout,yt_playlist_url))

		res,err = get_request_raw(yt_playlist_url)
		print("RESULT")
		print(res)
		if res==None:
			print("BDT - Error requesting playlist:")
			print(err)
			return None,err
		elif "items" in resn and len(res["items"])>0:
			print("grabbing items")
			[yt_playlist_contents.append(itm["contentDetails"]) for itm in res["items"] ]
			if "nextPageToken" not in res or res["nextPageToken"]=="":
				print("No more pages, breaking loop")
				break
			else:
				##### Something here not quite working right
				print("Yup, there's another page")
				nextPageToken = "&page="+res["nextPageToken"]
		else:
			print("BDT - items not found in request")
			print(res)
			return None,err
	
	print("EXITED PLAYLIST LOOP")
	print(yt_playlist_contents)

	# next, get the last video's ID 
	# (eventually, be able to select which index to get old tips)
	conf.jsn["subscribed_check_cache"]["yanal_sosak"] = yt_playlist_contents
	conf.jsn_save()

	# now get details of the video of interest
	# each of these even could be threaded for multiple image downloads
	def get_yt_video_info(yt_vid):
		baseurl = "https://www.googleapis.com/youtube/v3/videos?id="
		url = "{}{}&part=snippet&key={}".format(baseurl,yt_vid,fetch_yt_devkey())

		# first request, the data link itself
		res,err = get_request_raw(yt_playlist_url)
		if res==None:
			print("BDT - Error requesting playlist:")
			print(err)
			return None,err
		elif "items" in res and len(res["items"])>0:
			desc = res["items"][0]["snippet"]["description"]
			date = res["items"][0]["snippet"]["publishedAt"]
			title = res["items"][0]["snippet"]["title"]
		else:
			print("BDT - Did not receive expected data for video")
			print(res)
			return None,"Did not receive expected data for video"


		# only need this to get description/title/date
		# as we now know the icon download is, eg,
		yt_vidthumb_thumb = "https://i.ytimg.com/vi/{x}/mqdefault.jpg".format(x=yt_vid)
		# HQ, option
		#yt_vidthumb_img = "https://i.ytimg.com/vi/{x}/maxresdefault.jpg".format(x=yt_vid)

		# downlaod thumb by first seeing if it's locally there
		thmb = "ytthumb_"+yt_vid+"_"+yt_vidthumb_thumb.split("/")[-1]
		tmb_path = os.path.join(__file__,"icon_cache",thmb)
		
		if os.path.isfile(thmb)==False:
			try:
				urllib.request.urlretrieve(url, thmb)
			except Exception as e:
				print("BDT encountered an error downloading thumbnail")
				print(str(e))
				tmb_path = None
		else:
			if conf.verbose:
				print("BDT - skipped thumb {x} download, already local".format(
					x=yt_vid))

		ret = {"title":title,"description":desc,"date":date,
				"thumb":tmb_path,"url":vid_url}


	# now, finally run the above code to get latest tip
	yt_vid = yt_playlist_contents[-1]["videoId"] # error prone? check for "videoId"
	res, err = get_yt_video_info(yt_vid)
	return ret, err


def fetch_yt_devkey():
	global ytdevkey
	if ytdevkey != None:return ytdevkey

	# need to download youtube dev key
	return "_____LOAD_MANUALLY______"



# all API calls to base url
def get_request_raw(url):
	# returns: result, error
	request = urllib.request.Request(url)
	try:
		result = urllib.request.urlopen(request)
	except urllib.error.HTTPError as e:
		_error = "HTTP error with url: "+url
		_error_msg = str(e.code)
		print(_error)
		return None,"URL error, check internet connection. "+str(e)
	except urllib.error.URLError as e:
		_error = "URL error, check internet connection "+url
		_error_msg = str(e.reason)
		print(_error)
		return None,"URL error, check internet connection. "+str(e)
	else:
		result_string = result.read()
		result.close()

		# now
		try:
			tmp = json.loads(result_string.decode())
		except Exception as e:
			print("BDT - Exception, request url completed but failed to convert json; url: "+url)
			return None,"URL retreive json conversion error, "+str(e)

		return tmp,None


# -----------------------------------------------------------------------------
# ASYNC SETUP
# -----------------------------------------------------------------------------

# Launch a generic, self-terminating background thread
# func = the main function of this background loop
# arguments = tuple of function inputs
# returns true if thread started without issue
# (this is NOT related to whether the thread raises an error or not)
def launch_background_thread(func, arguments=None):
	if conf.async_progress != None:
		# avoid overlapping requests
		return
	if conf.verbose: print("BDT - Starting background thread")

	if arguments == None:
		arguments = ()

	argwrap = (func, arguments)

	new_thread = threading.Thread(target=thread_starter_func,args=argwrap)
	new_thread.daemon = True

	# protect starting of a thread, pass to UI if failed
	# note: this is only for starting a thread, not capturing
	# if the function itself err's out
	try:
		new_thread.start()
	except Exception as e:
		print("BDT - exception starting thread:")
		print(str(e))
		return str(e)

	
	return True


def check_tip_async(self,context):

	if conf.async_progress == True:
		# check for tips already in progress
		return ({"INFO"},"Please wait, still checking for tips...")
	elif conf.async_progress == False:
		# this shouldn't ever occur, but just in case
		conf.async_progress = None
		return ({"ERROR"},"Error occured: "+str(res))
	else:
		# normal course
		# consider starting two threads? 
		# one being a timeout and the other the actual thread
		# (timeout popup that is)


		res = launch_background_thread(bdt_fetch_tips)
		#res = launch_background_thread(bdt_fetch_tips, ("context") )
		if res == True:
			return ({"INFO"},"Checking for tips, please wait...")
		else:
			return ({"ERROR"},"Error occured: "+str(res))


def thread_starter_func(func,args):
	# run the function requested in a safe wrapper

	conf.async_progress = True
	if conf.failsafe==False:
		print("PRINTING BG ARGS")
		print(args)
		func(*args)
		conf.async_progress = None
	else:
		try:
			print("PRINTING BG ARGS")
			print(args)
			func(*args)
			conf.async_progress = None
			# callback handler is built in to args

		except Exception as e:
			print("BDT - Background thead exception:")
			print("\t"+str(e))
			conf.async_progress = None

			#exc_type, exc_obj, exc_tb = sys.exc_info()
			#fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			#print(exc_type, fname, exc_tb.tb_lineno)

			# throw on handler there was an error



def register():
	global ytdevkey
	ytdevkey = None # key for youtube api


def unregister():
	pass


