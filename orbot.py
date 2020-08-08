import random
import numpy as np

#Bot to simulate gravitational bodies
#made for BAS Hackathon 2020
#Author: Fuddlebob

G = 6.67e-8

class Body(object):
	def __init__(self, mass, position, velocity, id):
		self.mass = mass
		self.position = position
		self.velocity = velocity
		self.id = id
		
		
		
		
def main():
	bodies = []
	numBodies = random.randint(2, 2)
	print(numBodies)
	for i in (range(numBodies)):
		mass = random.uniform(1, 5)
		position = np.array([(random.random() - 0.5), (random.random() - 0.5)])
		velocity = np.array([(random.random() - 0.5), (random.random() - 0.5)]) / 100
		bodies.append(Body(mass, position, velocity, i))
		print("ID: " + str(i) + " Mass: " + str(mass) + " Position: " + str(position) + " Velocity: " + str(velocity))
	
	step(bodies)
	
	print("After one step:")
	for b in bodies:
		print("ID: " + str(b.id) + " Mass: " + str(b.mass) + " Position: " + str(b.position) + " Velocity: " + str(b.velocity))

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
		b.position = b.position + b.velocity
		
	return bodies






if (__name__ == '__main__'):
	main()