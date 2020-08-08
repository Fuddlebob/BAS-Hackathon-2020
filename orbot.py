import random
import numpy as np
import cv2
import math

#Bot to simulate gravitational bodies
#made for BAS Hackathon 2020
#Author: Fuddlebob

G = 6.67e-8
canvas_size = (480, 480, 3)

class Body(object):
	def __init__(self, mass, position, velocity, id, colour):
		self.mass = mass
		self.position = position
		self.velocity = velocity
		self.id = id
		self.colour = colour
		
		
		
		
def main():
	bodies = []
	numBodies = random.randint(2, 7)
	print(numBodies)
	for i in (range(numBodies)):
		mass = random.uniform(20, 200)
		position = np.array([(random.random() + 0.5), (random.random() + 0.5)])
		velocity = np.array([(random.random() - 0.5), (random.random() - 0.5)])
		colour = (random.randint(50, 255),random.randint(50, 255),random.randint(50, 255))
		bodies.append(Body(mass, position, velocity, i, colour))
	
	canvas = np.zeros(canvas_size, np.uint8)
	video_name = "vid.avi"
	vid = cv2.VideoWriter(video_name, 0, 20, (480, 480))
	clearcount = 0
	for i in range(600):
		bodies = step(bodies)
		im = render(bodies, canvas.copy())
		vid.write(im)
		if(not im.any()):
			clearcount += 1
			if(clearcount >= 10):
				break
		else:
			clearcount = 0
	vid.release()
		
	


def render(bodies, canvas):
	if(canvas is None):
		canvas = np.zeros(canvas_size, np.uint8)
	size = max(canvas_size[0], canvas_size[1])

	for b in bodies:
		x = int(((b.position[0] * size))/2)
		y = int(((b.position[1] * size))/2)
		canvas = cv2.circle(canvas, (x,y), mass2size(b.mass), b.colour, thickness=-1)
	return canvas
	

def mass2size(m):
	return int(math.sqrt((m * 10)/math.pi))
	
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
				pull = (G * b.mass * b2.mass) / (d * d)
				total = total + (pull * ndir)
		deltavs[b.id] = total	
	
	#update each velocity and apply the new velocity to the position
	for b in bodies:
		b.velocity = b.velocity + deltavs[b.id]
		b.position = b.position + (b.velocity / 50)
		
	return bodies






if (__name__ == '__main__'):
	main()