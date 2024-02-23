from function.car import car
import random

def randomLaneChange(carsA, carsB):
	a = len(carsA)-1
	b = len(carsB)-1
	carsA_after_laneChange = []
	carsB_after_laneChange = []
	carsA_after = []
	carsB_after = []
	while a >= 0 or b >= 0:
		if a < 0 and b >= 0:
			if random.randint(0,1) == 0:
				carsA_after_laneChange.append(carsB[b].id)
				carsA_after.append(carsB[b])
			else:
				carsB_after_laneChange.append(carsB[b].id)
				carsB_after.append(carsB[b])
			b -= 1
		elif b < 0 and a >= 0:
			carsA_after_laneChange.append(carsA[a].id)  
			carsA_after.append(carsA[a])   
			a -= 1
		else:
			if random.randint(0,1) == 0:
				if random.randint(0,1) == 0:
					carsA_after_laneChange.append(carsB[b].id) 
					carsA_after.append(carsB[b]) 
				else: 
					carsB_after_laneChange.append(carsB[b].id)
					carsB_after.append(carsB[b])
				b -= 1
			else:
				carsA_after_laneChange.append(carsA[a].id)
				carsA_after.append(carsA[a])
				a -= 1
		
	return carsA_after_laneChange, carsB_after_laneChange, len(carsB) - len(carsB_after_laneChange), carsA_after, carsB_after

def noLaneChange(carsA, carsB, lane_change_point, normal_speed):
	carsA_after_laneChange = []
	carsB_after_laneChange = []
	carsA_after = []
	carsB_after = []
	for i in range(len(carsA)-1, -1, -1):
		carsA[i].passChangeTime = lane_change_point / normal_speed + carsA[i].departTime
		carsA_after_laneChange.append(carsA[i].id)
		carsA_after.append(carsA[i])
	for i in range(len(carsB)-1, -1, -1):
		carsB[i].passChangeTime = lane_change_point / normal_speed + carsB[i].departTime
		carsB_after_laneChange.append(carsB[i].id)
		carsB_after.append(carsB[i])

	return carsA_after_laneChange, carsB_after_laneChange, 0, carsA_after, carsB_after

def allLaneChange(carsA, carsB, lane_change_point, normal_speed):
	cars = carsA + carsB
	cars.sort(key=lambda x: x.departTime, reverse=True)
	carsA_after_laneChange = []
	carsA_after = []
	carsB_after_laneChange = []
	carsB_after = []
	for car in cars:
		car.passChangeTime = lane_change_point / normal_speed + car.departTime
		carsA_after_laneChange.append(car.id)
		carsA_after.append(car)

	return carsA_after_laneChange, carsB_after_laneChange, len(carsB), carsA_after, carsB_after

def noWaitingLaneChange(carsA, carsB, lane_change_point, normal_speed, time_gap = 1):       
	cars = carsA + carsB
	cars.sort(key=lambda x: x.departTime, reverse=True)
	carsA_after_laneChange = []
	carsA_after = []
	carsB_after_laneChange = []
	carsB_after = []
	for i in range(len(cars)):
		if cars[i].id[0] == 'A':
			carsA_after_laneChange.append(cars[i].id)
			carsA_after.append(cars[i])
		else:
			front_gap = 1000000
			back_gap = 1000000
			if i+1 < len(cars):
				front_gap = cars[i].departTime - cars[i+1].departTime
			if i-1 >= 0:
				back_gap = cars[i-1].departTime - cars[i].departTime
			if front_gap >= time_gap and back_gap >= time_gap:
				carsA_after_laneChange.append(cars[i].id)
				carsA_after.append(cars[i])
			else:
				carsB_after_laneChange.append(cars[i].id)
				carsB_after.append(cars[i])


		cars[i].passChangeTime = lane_change_point / normal_speed + cars[i].departTime

	return carsA_after_laneChange, carsB_after_laneChange, len(carsB)-len(carsB_after_laneChange), carsA_after, carsB_after



