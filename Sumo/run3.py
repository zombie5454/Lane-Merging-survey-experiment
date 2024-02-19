import traci
from collections import defaultdict, deque
import random
import sys

# 這支程式是用來跑simulation
# 如何使用這個程式:
# 	1. 如果要跑一次simulation，記得把最後一行的run()給他uncommemt掉
#   2. 基本上跑python3 run3.py就能跑了
#	3. 如果要看simulation的過程，可以將441行的start_arg = ["sumo", "-c", "cfg.sumocfg"]中的"sumo"改成"sumo-gui"
#   4. python3 run3.py後可以加--c {lane-changing algorithm name: no(default), all, nowaiting, random} 
#	5. python3 run3.py後可以加--m {lane-merging algorithm name: fifo(default), random}
#	6. 注意 --c random 只能跟 --m random 一起用，因為prediction model不完善 
#   7. python3 run3.py後可以加new表示跑新的data(default不會生新data)，加last表示跑上次的simulation
#	8. 上次simulation的input的資料會寫進input.txt
#	9. 如果要print整個simulation所花費的step數，可以uncomment第627行(print(f'simulation end, it takes {step} steps'))

'''
import os, sys

if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("please declare environment variable 'SUMO_HOME'")

sys.path.append(os.path.join('c:', os.sep, 'whatever', 'path', 'to', 'sumo', 'tools'))
'''
############### functions for file and input ##############
class car:
	def __init__(self, id, departTime):
		self.id = id
		self.departTime = departTime
		self.passChangeTime = -1

	def printCar(self):
		print(f'car: id:{self.id}, departTime:{self.departTime}, passChangeTime:{self.passChangeTime}')

def printCars(cars):
	for car in cars:
		car.printCar()

def randomCar(departTimeA, departTimeB):
	carsA = []
	carsB = []
	for i in range(len(departTimeA)):
		carsA.append(car('A'+str(i), departTimeA[i]))
	for i in range(len(departTimeB)):
		carsB.append(car('B'+str(i), departTimeB[i]))

	return carsA, carsB, len(carsA)+len(carsB)

def randomDepartTime(numA = 4, numB = 4, mingap = 1, maxgap = 7):

	departTimeA = []	
	departTimeB = []
	departTimeA.append(random.randint(mingap, maxgap))
	departTimeB.append(random.randint(mingap, maxgap))
	for i in range(numA-1):
		if i == 0:			# 讓A車道的起始時間長一點
			departTimeA[0] += random.randint(mingap, maxgap)
		departTimeA.append(departTimeA[-1]+random.randint(mingap, maxgap))

	for i in range(numB-1):
		departTimeB.append(departTimeB[-1]+random.randint(mingap, maxgap))

	return departTimeA, departTimeB

def generateRoute(carsA, carsB):
	f_route = open('rou3.rou.xml', 'w')
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

############### algorithm ###############

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
		#carsA_after.reverse()
		#carsB_after.reverse()
	return carsA_after_laneChange, carsB_after_laneChange, len(carsB) - len(carsB_after_laneChange), carsA_after, carsB_after

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

def noLaneChange(carsA, carsB, lane_change_point):
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

def allLaneChange(carsA, carsB, lane_change_point):
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

def noWaitingLaneChange(carsA, carsB, lane_change_point, time_gap = 1):       
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



def FIFO(carsA_after, carsB_after):
	passingOrder = []
	cars = carsA_after + carsB_after
	cars.sort(key=lambda x: x.departTime, reverse=True)
	#printCars(cars)
	for i in cars:
		passingOrder.append(i.id)
	return passingOrder


############### functions for scenario ##########

def lane_merge(step, 
	passing_order,  
	W_equal, 
	W_plus, 
	last_passing_step, 
	last_passing_lane, 
	last_laneA_id, 
	last_laneB_id, 
	tail_has_stop,
	laneA_id, 
	laneB_id,
	car_done,
	merging_count,
	merging_num):

	#initially set stop and speed
	if laneA_id[0] != 'N':
		if last_laneA_id[0] != laneA_id[0] or last_laneA_id[0] == 'N':
			traci.vehicle.setStop(laneA_id[0], 'E1_A', pos=247)
			#traci.vehicle.setStop(laneA_id[0], 'E1_A', pos=200)
			#traci.vehicle.setStop(laneA_id[0], 'E1_A', pos=200, duration=0)
			#print('set stop to ', laneA_id[0])
			
	if laneB_id[0] != 'N':
		if last_laneB_id[0] != laneB_id[0] or last_laneB_id[0] == 'N':
			traci.vehicle.setStop(laneB_id[0], 'E1_B', pos=247)
			#traci.vehicle.setStop(laneB_id[0], 'E1_B', pos=200)
			#traci.vehicle.setStop(laneB_id[0], 'E1_B', pos=200, duration=0)
			#print('set stop to ', laneB_id[0])
			
	# When a vehicle done a passing
	if last_laneA_id[0] != 'N' and last_laneA_id[-1] != laneA_id[-1]:
		last_passing_step = step
		tail_has_stop = True
		car_done[last_laneA_id[-1]] = True
		passing_order.pop()
		merging_count += 1
	if last_laneB_id[0] != 'N' and last_laneB_id[-1] != laneB_id[-1]:
		last_passing_step = step
		tail_has_stop = True
		car_done[last_laneA_id[-1]] = True
		passing_order.pop()
		merging_count += 1


	if merging_count == merging_num:  #all cars passed
		return last_passing_step, last_passing_lane, tail_has_stop, merging_count


	# determine whether the tail will pass
	if tail_has_stop == True and len(passing_order) >= 1:
		next_pass_id = passing_order[-1]
		tail = 'N'
		if next_pass_id == laneA_id[-1]:
			tail = laneA_id[-1]
		elif next_pass_id == laneB_id[-1]:
			tail = laneB_id[-1]

		#print(tail)
		if tail == 'N':
			return last_passing_step, last_passing_lane, tail_has_stop, merging_count
		#print(traci.vehicle.getRoadID(tail))

		if tail != 'N' and traci.vehicle.getRoadID(tail)[-1] == last_passing_lane[-1] and step - last_passing_step >= W_equal:    #same lane
			if traci.vehicle.getRoadID(tail)[-1] == 'A':
				traci.vehicle.setStop(tail, 'E1_A', pos=247, duration = 0)
				last_passing_lane = traci.vehicle.getRoadID(tail)
			else:
				traci.vehicle.setStop(tail, 'E1_B', pos=247, duration = 0)
				last_passing_lane = traci.vehicle.getRoadID(tail)
			#print('del stop of ', tail)
			tail_has_stop = False

		elif tail != 'N' and traci.vehicle.getRoadID(tail)[-1] != last_passing_lane[-1] and step - last_passing_step >= W_plus:    #dif lane
			if traci.vehicle.getRoadID(tail)[-1] == 'A':
				traci.vehicle.setStop(tail, 'E1_A', pos=247, duration = 0)
				last_passing_lane = traci.vehicle.getRoadID(tail)
			else:
				traci.vehicle.setStop(tail, 'E1_B', pos=247, duration = 0)
				last_passing_lane = traci.vehicle.getRoadID(tail)
			#print('del stop of ', tail)
			tail_has_stop = False
	return last_passing_step, last_passing_lane, tail_has_stop, merging_count

'''
def change_lane(safe_dis, laneA_c, laneB_c, laneA_id, lane_change_point, step_error):
	if laneB_c[-1] != 'N':
		now_dis = traci.vehicle.getLanePosition(laneB_c[-1])
		#print(now_dis)
		if now_dis >= lane_change_point - step_error:
			front_dis = 100000
			back_dis = -100000
			if laneA_id[0] != 'N':
				front_dis = traci.vehicle.getLanePosition(laneA_id[0])
			if laneA_c[-1] != 'N':
				back_dis = traci.vehicle.getLanePosition(laneA_c[-1])
			print('front_dis = ', front_dis)
			print('back_dis = ', back_dis)
			if now_dis - back_dis >= safe_dis and front_dis >= safe_dis:
				traci.vehicle.setRouteID(laneB_c[-1], 'rB_c')
	return
'''


def change_lane_order(safe_dis, front_car_laneA, car_done, laneA_c, laneB_c, laneA_after_change, last_laneA_c, last_laneB_c, tail_has_stop_c, laneA_id, changing_count, changing_num):

	#initially set stop
	if len(laneA_after_change) == 0:
		return tail_has_stop_c, changing_count

	if laneA_c[0] != 'N':
		if last_laneA_c[0] != laneA_c[0] or last_laneA_c[0] == 'N':
			traci.vehicle.setStop(laneA_c[0], 'E0_A', pos=247-safe_dis)
			#traci.vehicle.setStop(laneA_c[0], 'E0_A', pos=100)
			#traci.vehicle.setStop(laneA_c[0], 'E0_A', pos=100, duration=0)
			#print('set stop to ', laneA_c[0])
			#print(traci.vehicle.getStops(laneA_c[0], limit=0))
	if laneB_c[0] != 'N':
		if last_laneB_c[0] != laneB_c[0] or last_laneB_c[0] == 'N':
			if traci.vehicle.getRouteID(laneB_c[0]) == 'rB_c':					#only set stops to cars in laneB that will change lane 
				traci.vehicle.setStop(laneB_c[0], 'E0_B', pos=247)
				#traci.vehicle.setStop(laneB_c[0], 'E0_B', pos=100)
				#traci.vehicle.setStop(laneB_c[0], 'E0_B', pos=100, duration=0)
				#print('set stop to ', laneB_c[0])
				#print(traci.vehicle.getStops(laneB_c[0], limit=0))
				
	
	# determine whether the tail will pass
	if laneA_c[-1] == laneA_after_change[-1] and tail_has_stop_c == True:
		traci.vehicle.setStop(laneA_c[-1], 'E0_A', pos=247-safe_dis, duration = 0)
		traci.vehicle.setMaxSpeed(laneA_c[-1], normal_speed)      # in case of slowing down
		#print(f'set {laneA_c[-1]} MaxSpeed to {normal_speed}')
		#print('del stop of ', laneA_c[-1])
		#print(traci.vehicle.getStops(laneA_c[-1], limit=0))
		tail_has_stop_c = False

	front_dis = -100000
	front_car = front_car_laneA[laneB_c[-1]]
	#print(front_car)
	if car_done[front_car] or front_car == 'N':
		front_dis = 10000000
	elif traci.vehicle.getRoadID(front_car) == '':
		front_dis = traci.vehicle.getLanePosition(front_car)
	elif traci.vehicle.getRoadID(front_car)[1] == '1' :
		front_dis = traci.vehicle.getLanePosition(front_car)
	
	if laneB_c[-1] == laneA_after_change[-1] and tail_has_stop_c == True and front_dis >= 0:
		traci.vehicle.setStop(laneB_c[-1], 'E0_B', pos=247, duration = 0)
		#print('del stop of ', laneB_c[-1])
		#traci.vehicle.setMaxSpeed(laneB_c[-1], normal_speed)		# in case of slowing down
		#print(f'set {laneB_c[-1]} MaxSpeed to {normal_speed}')
		#print(traci.vehicle.getStops(laneB_c[-1], limit=0))
		tail_has_stop_c = False
	
	if len(laneA_after_change) == 0:
		return tail_has_stop_c, changing_count
	# When a vehicle done a passing
	if last_laneA_c[-1] != 'N' and laneA_c[-1] != last_laneA_c[-1]:
		laneA_after_change.pop()
		tail_has_stop_c = True
		changing_count += 1

	if len(laneA_after_change) == 0:
		return tail_has_stop_c, changing_count
	if last_laneB_c[-1] != 'N' and laneB_c[-1] != last_laneB_c[-1] and last_laneB_c[-1] == laneA_after_change[-1]:
		laneA_after_change.pop()
		tail_has_stop_c = True
		changing_count += 1

	return tail_has_stop_c, changing_count
	

def slow_down(detA, detB, last_detA, last_detB, front_car_laneA, car_done):
	front_car = front_car_laneA[detB[0]]
	front_dis = 1000000
	if front_car != 'N' and car_done[front_car] == False:

		if traci.vehicle.getRoadID(front_car) == '' or traci.vehicle.getRoadID(front_car)[1] == '-':  # roadID == '' means car doesn't existed yet
			front_dis = -100000
		elif traci.vehicle.getRoadID(front_car)[1] == '0':
			front_dis = traci.vehicle.getLanePosition(front_car)
	
	if detB[0] != 'N' and detB[0] != last_detB[0]:
		if front_dis - traci.vehicle.getLanePosition(detB[0]) <= safe_dis:
			traci.vehicle.setMaxSpeed(detB[0], slow_speed)
			#print(f'set {detB[0]} maxSpeed to {slow_speed}') 

	
	front_car = front_car_laneA[detA[0]]
	front_dis = 1000000
	if front_car != 'N' and car_done[front_car] == False:
		if traci.vehicle.getRoadID(front_car) == '' or traci.vehicle.getRoadID(front_car)[1] == '-':  # roadID == '' means car doesn't existed yet
			front_dis = -100000
		elif traci.vehicle.getRoadID(front_car)[1] == '0':
			front_dis = traci.vehicle.getLanePosition(front_car)

	if detA[0] != 'N' and detA[0] != last_detA[0]:
		if front_dis - traci.vehicle.getLanePosition(detA[0]) <= safe_dis:
			traci.vehicle.setMaxSpeed(detA[0], slow_speed)
			#rint(f'set {detA[0]} maxSpeed to {slow_speed}')
	return 
		
################## main function #####################

#### global variable ####
lane_change_point = 250
normal_speed = 14  # 14 m/s = 50.4 km/hr
W_equal = normal_speed * 1
W_plus = normal_speed * 3
safe_dis = normal_speed * 2
slow_speed = normal_speed * 0.6
step_error = normal_speed * 0.1
time_gap = safe_dis / normal_speed

def run(arg = sys.argv, Wequal = normal_speed * 1, Wplus = normal_speed * 3, numA = 4, numB = 4):
	# option, argv

	step_length = 0.1		#sumo/sumo-gui use a time step of one second per default. You may override this using the --step-length <TIME> option. <TIME> is by giving a value in seconds between [0.001 and 1.0].
	start_arg = ["sumo-gui", "-c", "cfg.sumocfg"]
	lane_change_alg = 'No'
	lane_merge_alg = 'FIFO'
	new_data = False
	last_simulation = False
	for i in range(1, len(arg)):
		#print(arg[i])
		if arg[i] == '--step-length' or arg[i] == '--sl':
			step_length = arg[i+1]
		if arg[i] == '--c':
			lane_change_alg = arg[i+1]
		if arg[i] == '--m':
			lane_merge_alg = arg[i+1]
		if arg[i] == 'new':
			new_data = True
		if arg[i] == 'last':
			last_simulation = True


	start_arg.append('--step-length')
	start_arg.append(str(step_length))
	start_arg.append('--no-step-log')



	#### given variable ####
	lane_change_point = 250
	normal_speed = 14  # 14 m/s = 50.4 km/hr
	W_equal = Wequal
	W_plus = Wplus

	safe_dis = normal_speed * 2
	slow_speed = normal_speed * 0.6
	step_error = normal_speed * step_length
	time_gap = safe_dis / normal_speed



	# read last simulation's input
	f = open('input.txt', 'r')
	inputs = f.readlines()
	f.close()
	#print(inputs)
	for i in range(4):
		if i >= 2:
			inputs[i] = inputs[i].strip("[]\n'").split("', '")
		if i < 2:
			inputs[i] = inputs[i].strip('[]\n').split(',')
			inputs[i] = list(map(float, inputs[i]))
	if new_data:
		departTimeA, departTimeB = randomDepartTime(mingap = time_gap, numA=numA, numB=numB)
	else:
		departTimeA = inputs[0]
		departTimeB = inputs[1]
	#print('depart timeA: ', departTimeA)
	#print('depart timeB: ', departTimeB)
	carsA, carsB, merging_num = randomCar(departTimeA, departTimeB)
	generateRoute(carsA, carsB)
	
	if lane_change_alg.lower() == 'no':
		laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = noLaneChange(carsA, carsB, lane_change_point)
	elif lane_change_alg.lower() == 'all':
		laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = allLaneChange(carsA, carsB, lane_change_point)
	elif lane_change_alg.lower() == 'nowaiting':
		laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = noWaitingLaneChange(carsA, carsB, lane_change_point, time_gap)
	elif lane_change_alg.lower() == 'random':
		laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = randomLaneChange(carsA, carsB)    # the order on laneA/laneB after lane-change point
	else:
		print('lane_change_alg invalid')
		sys.exit()
	
	
	if lane_merge_alg.lower() == 'fifo':
		passing_order = FIFO(carsA_after, carsB_after)
	elif lane_merge_alg.lower() == 'random':
		passing_order = randomPassingOrder(carsA_after, carsB_after)
	else:
		print('lane_merge_alg invalid')
		sys.exit()
	

	#laneA_after_change = inputs[2]
	#passing_order = inputs[3]
	#print('laneA_after_change:', laneA_after_change)
	#print('passing_order: ', passing_order)

	# write this simulation's input
	inputs[0] = departTimeA
	inputs[1] = departTimeB
	inputs[2] = laneA_after_change
	inputs[3] = passing_order
	f = open('input.txt', 'w')
	for i in range(4):
		f.write(str(inputs[i]))
		f.write('\n')
	f.write('# depart timeA\n# depart timeB\n# laneA_after_change\n# passing_order\n')
	f.close()

	step = 0
	traci.start(start_arg)

	#### functional variable ####
	last_passing_step = -1000
	last_passing_lane = 'A'
	last_laneA_id = ['N'] # 'N' means empty
	last_laneB_id = ['N']
	tail_has_stop = True
	last_laneA_c = ['N']
	last_laneB_c = ['N']
	tail_has_stop_c = True
	front_car_laneA = defaultdict(lambda: 'N')   # save the front car of a car in laneA after lane change
	for i, car in enumerate(laneA_after_change):
		if car[0] == 'B':
			traci.vehicle.setRouteID(car, 'rB_c')	# change route of cars in laneB that will lane-change
		if i+1 < len(laneA_after_change):
			front_car_laneA[car] = laneA_after_change[i+1]
	last_detA = 'N'
	last_detB = 'N'
	car_done = defaultdict(lambda: False) #cars that pass the merging point
#print(merging_num, changing_num)
	merging_count = 0
	changing_count = 0
	#print(f'lane_change_alg: {lane_change_alg}')
	#print(f'lane_merge_alg: {lane_merge_alg}')

	while step < 10000000:

		step += 1
		#print('step: ', step)
		traci.simulationStep()
	
		if merging_count == merging_num:
			break
	
		laneA_id = list(traci.edge.getLastStepVehicleIDs('E1_A'))
		laneB_id = list(traci.edge.getLastStepVehicleIDs('E1_B'))
		laneA_c = list(traci.edge.getLastStepVehicleIDs('E0_A'))
		laneB_c = list(traci.edge.getLastStepVehicleIDs('E0_B'))

		if len(laneA_id) == 0: # 'N' means empty
			laneA_id.append('N')
		if len(laneB_id) == 0:
			laneB_id.append('N')
		if len(laneA_c) == 0: # 'N' means empty
			laneA_c.append('N')
		if len(laneB_c) == 0:
			laneB_c.append('N')
		#print('laneA_id = ', laneA_id)
		#print('laneB_id = ', laneB_id)

		#change_lane(safe_dis, laneA_c, laneB_c, laneA_id, lane_change_point, step_error)
		tail_has_stop_c, changing_count = change_lane_order(safe_dis, front_car_laneA, car_done, laneA_c, laneB_c, laneA_after_change, 
			last_laneA_c, last_laneB_c, tail_has_stop_c, laneA_id, changing_count, changing_num)

		last_passing_step, last_passing_lane, tail_has_stop, merging_count = lane_merge(step=step, 
			passing_order=passing_order,   # a pass first, and then a, and then b, ...
			W_equal=W_equal, 
			W_plus=W_plus, 
			last_passing_step=last_passing_step, 
			last_passing_lane=last_passing_lane, 
			last_laneA_id=last_laneA_id, 
			last_laneB_id=last_laneB_id, 
			tail_has_stop=tail_has_stop,
			laneA_id=laneA_id,
			laneB_id=laneB_id, 
			car_done=car_done,
			merging_count=merging_count,
			merging_num=merging_num)
	
		detB = list(traci.inductionloop.getLastStepVehicleIDs('detB'))
		detA = list(traci.inductionloop.getLastStepVehicleIDs('detA'))
		if len(detB) == 0: # 'N' means empty
			detB.append('N')
		if len(detA) == 0:
			detA.append('N')

		#slow_down(detA, detB, last_detA, last_detB, front_car_laneA, car_done)
	
		last_detA = detA
		last_detB = detB
		last_laneA_id = laneA_id
		last_laneB_id = laneB_id
		last_laneA_c = laneA_c
		last_laneB_c = laneB_c


	#print(f'simulation end, it takes {step} steps')
	traci.close()
	return step

run()
