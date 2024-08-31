from Model.Car import Car
import random

def randomDepartTime(numA = 4, numB = 4, mingap = 1, maxgap = 7):
	departTimeA: list[int] = []	
	departTimeB: list[int] = []
	departTimeA.append(random.randint(mingap, maxgap))
	departTimeB.append(random.randint(mingap, maxgap))
	for i in range(numA-1):
		if i == 0:			# 讓A車道的起始時間長一點
			departTimeA[0] += random.randint(mingap, maxgap)
		departTimeA.append(departTimeA[-1]+random.randint(mingap, maxgap))

	for i in range(numB-1):
		departTimeB.append(departTimeB[-1]+random.randint(mingap, maxgap))

	return departTimeA, departTimeB



def randomCar(departTimeA, departTimeB):
	carsA: list[Car] = []
	carsB: list[Car] = []
	for i in range(len(departTimeA)):
		carsA.append(Car('A'+str(i), departTimeA[i]))
	for i in range(len(departTimeB)):
		carsB.append(Car('B'+str(i), departTimeB[i]))

	return carsA, carsB, len(carsA)+len(carsB)



def generateRoute(carsA, carsB):
	f_route = open('Setup/rou3.rou.xml', 'w')
	f_route.write('<routes>\n')
	f_route.write('\t<vType id="car" accel="5" decel="7" sigma="0" length="5" maxSpeed="14"/>\n')
	f_route.write('\t<route id="rA" edges="E-1_A E0_A E1_A E2"/>\n')
	f_route.write('\t<route id="rB" edges="E-1_B E0_B E1_B E2"/>\n')
	f_route.write('\t<route id="rB_c" edges="E-1_B E0_B E1_A E2"/>\n')
	for car in carsA:
		f_route.write('\t<vehicle id="' + car.id + '" color="0,1,1" depart="0" route="rA" type = "car" departPos="47">\n')
		f_route.write('\t\t<stop lane="E-1_A_0" endPos="-1" until="' + str(car.departTime) + '"/>\n')
		f_route.write('\t</vehicle>\n')
	for car in carsB:
		f_route.write('\t<vehicle id="' + car.id + '" color="1,0,0" depart="0" route="rB" type = "car" departPos="47">\n')
		f_route.write('\t\t<stop lane="E-1_B_0" endPos="-1" until="' + str(car.departTime) + '"/>\n')
		f_route.write('\t</vehicle>\n')
	f_route.write('</routes>\n')
	f_route.close()
	return