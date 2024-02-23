from function.car import car, printCars
import random

def randomPassingOrder(carsA_after, carsB_after):
	a = 0
	b = 0
	la = len(carsA_after)
	lb = len(carsB_after)  
	passingOrder = []
	while a < la or b < lb:
		if a >= la and b < lb:
			passingOrder.append(carsB_after[b].id)
			b += 1
		elif b >= lb and a < la:
			passingOrder.append(carsA_after[a].id)
			a += 1
		else:
			if random.randint(0,1) == 0:
				passingOrder.append(carsB_after[b].id)
				b += 1
			else:
				passingOrder.append(carsA_after[a].id)
				a += 1
	return passingOrder



def FIFO(carsA_after, carsB_after):
	passingOrder = []
	cars = carsA_after + carsB_after
	cars.sort(key=lambda x: x.departTime, reverse=True)
	#printCars(cars)
	for i in cars:
		passingOrder.append(i.id)
	return passingOrder