import random
import numpy as np
import cv2
import math
import copy
import requests
import os
import subprocess
import sys
import jsonreader
#Bot to simulate gravitational bodies
#made for BAS Hackathon 2020
#Author: Fuddlebob

#in real life this is 6.67e-11 but luckily these are made up units so I can make it whatever the hell I want
G = 6.67e-1

#read in config file
if(len(sys.argv) > 1):
	cfg = jsonreader.Reader(sys.argv[1])
else:
	print("Please provide a configuration file")
	sys.exit(1)

FB_TOKEN = cfg["fb_token"]
post_to_fb = cfg["upload"]
canvas_width = cfg["canvas_width"]
canvas_height = cfg["canvas_height"]
canvas_size = (canvas_height, canvas_width, 3)
avi_out = cfg["avi_out"]
mp4_out = cfg["mp4_out"]
timesteps_per_frame = cfg["timesteps"]

FACEBOOK_MEDIA_ENDPOINT_URL = 'https://graph-video.facebook.com/me/videos'

class Body(object):
	def __init__(self, mass, position, velocity, id, colour):
		self.mass = mass
		self.position = position
		self.velocity = velocity
		self.id = id
		self.colour = colour
		
		
		
		
def main():
	#first, remove existing files
	print("Removing files...")
	remove_files()
	bodies = []
	numBodies = random.randint(3, 18)
	print("Initilising...")
	for i in (range(numBodies)):
		mass = 0
		while (mass <= 0):
			mass = random.gauss(150, 120) 
		position = np.array([(random.random() * canvas_height * 0.75) + 0.125 * canvas_height, (random.random() * canvas_width * 0.75) + 0.125 * canvas_width])
		velocity = np.array([(random.random() - 0.5) * 12, (random.random() - 0.5) * 12])
		colour = (random.randint(100, 255),random.randint(100, 255),random.randint(100, 255))
		bodies.append(Body(mass, position, velocity, i, colour))
		
	
	#determine camera offset so camera is centered better
	tot = np.array([0,0])
	for b in bodies:
			tot = tot + b.position
	av = tot / numBodies
	#subtract average from each body position, then add center of canvas
	#also construct the fb message here while we're at it
	fb_message = ""
	for b in bodies:
		b.position = b.position - av + np.array([canvas_height/2, canvas_width/2])
		fb_message = fb_message + "Planet {0}: Mass: {1:.2f}, Starting Position: ({2:.2f}, {3:.2f}), Starting Velocity ({4:.2f}, {5:.2f})\n".format(b.id + 1, b.mass, b.position[1], b.position[0], b.velocity[1], b.velocity[0])
	print(fb_message)
	canvas = np.zeros(canvas_size, np.uint8)
	vid = cv2.VideoWriter(avi_out, 0, 20, (canvas_size[1], canvas_size[0]))
	clearcount = 0
	print("Rendering steps...")
	#start performing timesteps and rendering images
	for i in range(600):
		canvas = (canvas * 0.99).astype(np.uint8)
		for j in range(timesteps_per_frame):
			oldBodies = copy.deepcopy(bodies)
			bodies = step(bodies)
			canvas = mark_path(oldBodies, bodies, canvas)
		im = render(bodies, canvas.copy())
		#immediately write the image to the video
		vid.write(im)
		#if the screen is appropriately dark for long enough, end early
		if((im < 30).all()):
			clearcount += 1
			if(clearcount >= 20):
				break
		else:
			clearcount = 0
	#save the video
	vid.release()
	#convert to mp4 for smaller file size
	print("Converting to mp4...")
	with open(os.devnull, 'w') as shutup:
		subprocess.call(['ffmpeg', '-y', '-i', avi_out, '-ac', '2', '-b:v', '2000k', '-c:a', 'aac',  
			'-c:v', 'libx264', '-b:a', '160k', '-vprofile', 'high', '-bf',
			'0', '-strict', 'experimental', '-f', 'mp4', mp4_out], stdout=shutup, stderr=shutup)
	
	#finally, post to facebook
	if(post_to_fb):
		print("Posting to Facebook...")
		upload_to_facebook(mp4_out, fb_message)
		
def remove_files():
	#removes files
	if os.path.exists(avi_out):
		os.remove(avi_out)
	if os.path.exists(mp4_out):
		os.remove(mp4_out)


#draws a bunch of fuckin circles
def render(bodies, canvas):
	if(canvas is None):
		canvas = np.zeros(canvas_size, np.uint8)

	for b in bodies:
		pos = (int(b.position[1]), int(b.position[0]))
		canvas = cv2.circle(canvas, pos, mass2size(b.mass), b.colour, thickness=-1)
	return canvas
	
#marks the path that each body took in between steps
def mark_path(oldBodies, newBodies, canvas):
	for i in range(len(oldBodies)):
		#need to reverse the x/y because numpy is stupid
		oldpos = (int(oldBodies[i].position[1]), int(oldBodies[i].position[0]))
		newpos = (int(newBodies[i].position[1]), int(newBodies[i].position[0]))
		canvas = cv2.line(canvas, oldpos, newpos, oldBodies[i].colour, thickness = 2)
	
	return canvas
	
#converts planet mass to circle radius
def mass2size(m):
	return int(math.sqrt((m * 7)/math.pi))

#calculates distance between two points
def dist(p1, p2):
	return np.linalg.norm(p1 - p2)

#calculates and applies movement for a single timestep
def step(bodies):
	#calculate gravitational pull from each body
	deltavs = {}
	for b in bodies:
		total = np.array([0, 0])
		for b2 in bodies:
			if(not b == b2):
				d = dist(b2.position, b.position)
				dir = b2.position - b.position
				if(d == 0):
					ndir = dir
				else:
					ndir = dir/d
				#calculate gravitational pull
				#F = (G*m1*m2)/d^2
				#m1 cancels out when we solve for acceleration (F = ma, a = F/m)
				pull = (G * b2.mass) / (d * d)
				total = total + (pull * ndir)
		deltavs[b.id] = total	
	
	#update each velocity and apply the new velocity to the position
	for b in bodies:
		b.velocity = b.velocity + deltavs[b.id]
		b.position = b.position + (b.velocity)
		
	return bodies.copy()

#uploads vidname to facebook, with message
def upload_to_facebook(vidname, message):
	files={'file':open(vidname,'rb')}
	params = (
		('access_token', FB_TOKEN),
		('description', message)
	)	
	response = requests.post(FACEBOOK_MEDIA_ENDPOINT_URL, params=params, files=files)
	print(str(response.content))
	return response.json()["id"]



if (__name__ == '__main__'):
	main()