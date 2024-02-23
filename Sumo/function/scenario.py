import traci
from collections import defaultdict, deque
import sys
from function.car import car, printCars
from function.generateInput import randomDepartTime, randomCar, generateRoute
from function.laneChange import randomLaneChange, noLaneChange, allLaneChange, noWaitingLaneChange
from function.passingOrder import randomPassingOrder, FIFO
from function.action import lane_merge, change_lane_order, slow_down

### scenario是用來模擬整體架構的class，其中的run()可以用來跑一次simulation ###

# 1.可以透過set_gui()來讓simulation的過程呈現在內建的GUI上
# 2.可以透過set_numA()和set_numB()來決定A, B車道上的車輛數
# 3.可以透過set_printSteps()來讓print出simulation所花的step數
# 4.在跑run()時，傳入的參數arg: List，請注意arg[0]是不會讀取到的，所以建議是用sys.argv傳入
# 5.arg的option有: 
#		--c [lane-changing演算法]，lane-changing演算法有: no(default), all, nowaiting, random
#		--m [lane-merging演算法],  lane-merging演算法有: fifo(default), random
#		--step-length [n] or --sl [n], 數字介於[0.001 and 1.0]，表示一個step代表實際幾秒, default: 0.1
# 		new, 代表需要新的data
# 6.重要的varibale的初始值和default值都在__init__()裡
# 7.input.txt會儲存上一次跑的simulation的input

'''
import os, sys

if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("please declare environment variable 'SUMO_HOME'")

sys.path.append(os.path.join('c:', os.sep, 'whatever', 'path', 'to', 'sumo', 'tools'))
'''

class scenario:
	def __init__(self):
		# option, argv
		self.step_length = 0.1		# sumo/sumo-gui use a time step of one second per default. You may override this using the --step-length <TIME> option. <TIME> is by giving a value in seconds between [0.001 and 1.0].
		self.start_arg = ["sumo", "-c", "cfg.sumocfg"] 
		self.lane_change_alg = 'No'
		self.lane_merge_alg = 'FIFO'
		self.new_data = False
		self.printSteps = False


		# variable
		self.lane_change_point = 250
		self.normal_speed = 14  	# 14 m/s = 50.4 km/hr
		self.safe_dis = self.normal_speed * 2
		self.slow_speed = self.normal_speed * 0.6
		self.step_error = self.normal_speed * self.step_length
		self.time_gap = self.safe_dis / self.normal_speed
		self.W_equal = self.normal_speed * 1
		self.W_plus = self.normal_speed * 3
		self.numA = 4
		self.numB = 4



	#### setter ####
	def set_printSteps(self):
		self.printSteps = True

	def unset_printSteps(self):
		self.printSteps = False	

	def set_gui(self):
		self.start_arg[0] = "sumo-gui"

	def unset_gui(self):
		self.start_arg[0] = "sumo"

	def set_W_equal(self, w):
		self.W_equal = w

	def set_W_plus(self, w):
		self.W_plus = w

	def set_numA(self, n):
		self.numA = n

	def set_numB(self, n):
		self.numB = n	



	def run(self, arg):	
	
		#### option, argv ####
		step_length = self.step_length		# sumo/sumo-gui use a time step of one second per default. You may override this using the --step-length <TIME> option. <TIME> is by giving a value in seconds between [0.001 and 1.0].
		start_arg = self.start_arg.copy()
		lane_change_alg = self.lane_change_alg
		lane_merge_alg = self.lane_merge_alg
		new_data = self.new_data
		for i in range(1, len(arg)):
			if arg[i] == '--step-length' or arg[i] == '--sl':
				step_length = arg[i+1]
			if arg[i] == '--c':
				lane_change_alg = arg[i+1]
			if arg[i] == '--m':
				lane_merge_alg = arg[i+1]
			if arg[i] == 'new':
				new_data = True

		start_arg.append('--step-length')
		start_arg.append(str(step_length))
		start_arg.append('--no-step-log')
	

	
		departTimeA = []
		departTimeB = []
		if new_data:
			departTimeA, departTimeB = randomDepartTime(mingap = self.time_gap, numA=self.numA, numB=self.numB)	
			
		else:		
			f = open('input.txt', 'r')
			inputs = f.readlines()
			f.close()
			for i in range(4):		
				if i >= 2:
					inputs[i] = inputs[i].strip("[]\n'").split("', '")
				if i < 2:
					inputs[i] = inputs[i].strip('[]\n').split(',')
					inputs[i] = list(map(float, inputs[i]))
			departTimeA = inputs[0]
			departTimeB = inputs[1]	


		carsA, carsB, merging_num = randomCar(departTimeA, departTimeB)
		generateRoute(carsA, carsB)



		laneA_after_change = []
		laneB_after_change = []
		carsA_after = []
		carsB_after = []
		changing_num = -1
		if lane_change_alg.lower() == 'no':
			laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = noLaneChange(carsA, carsB, self.lane_change_point, self.normal_speed)
		elif lane_change_alg.lower() == 'all':
			laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = allLaneChange(carsA, carsB, self.lane_change_point, self.normal_speed)
		elif lane_change_alg.lower() == 'nowaiting':
			laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = noWaitingLaneChange(carsA, carsB, self.lane_change_point, self.normal_speed, self.time_gap)
		elif lane_change_alg.lower() == 'random':
			laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = randomLaneChange(carsA, carsB)   
		else:
			print('lane_change_alg invalid')
			sys.exit()
	
	

		passing_order = []
		if lane_merge_alg.lower() == 'fifo':
			passing_order = FIFO(carsA_after, carsB_after)
		elif lane_merge_alg.lower() == 'random':
			passing_order = randomPassingOrder(carsA_after, carsB_after)
		else:
			print('lane_merge_alg invalid')
			sys.exit()
	


		# write this simulation's input
		inputs = [0] * 4
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
	


		#### functional variable ####
		last_passing_step = -1000
		last_passing_lane = 'A'
		last_laneA_id = ['N'] 		# 'N' means empty
		last_laneB_id = ['N']
		tail_has_stop = True
		last_laneA_c = ['N']
		last_laneB_c = ['N']
		tail_has_stop_c = True
		front_car_laneA = defaultdict(lambda: 'N')   	# save the front car of a car in laneA after lane change
		last_detA = 'N'
		last_detB = 'N'
		merging_count = 0
		changing_count = 0



		#### start stimulation ####
		step = 0
		traci.start(start_arg)

		for i, car in enumerate(laneA_after_change):
			if car[0] == 'B':
				#print(car)
				traci.vehicle.setRouteID(car, 'rB_c')		# change route of cars in laneB that will lane-change
			if i+1 < len(laneA_after_change):
				front_car_laneA[car] = laneA_after_change[i+1]
		
		car_done = defaultdict(lambda: False) 		#cars that pass the merging point
		
		while step < 10000000:

			step += 1
			traci.simulationStep()
	
			if merging_count == merging_num:
				break
	
			laneA_id = list(traci.edge.getLastStepVehicleIDs('E1_A'))
			laneB_id = list(traci.edge.getLastStepVehicleIDs('E1_B'))
			laneA_c = list(traci.edge.getLastStepVehicleIDs('E0_A'))
			laneB_c = list(traci.edge.getLastStepVehicleIDs('E0_B'))

			if len(laneA_id) == 0: 		# 'N' means empty
				laneA_id.append('N')
			if len(laneB_id) == 0:
				laneB_id.append('N')
			if len(laneA_c) == 0: 		# 'N' means empty
				laneA_c.append('N')
			if len(laneB_c) == 0:
				laneB_c.append('N')

			#change_lane(self.safe_dis, laneA_c, laneB_c, laneA_id, self.lane_change_point, self.step_error)
			tail_has_stop_c, changing_count = change_lane_order(self.safe_dis, front_car_laneA, car_done, laneA_c, laneB_c, laneA_after_change, 
				last_laneA_c, last_laneB_c, tail_has_stop_c, laneA_id, changing_count, changing_num, self.normal_speed)

			last_passing_step, last_passing_lane, tail_has_stop, merging_count = lane_merge(step=step, 
				passing_order=passing_order,  
				W_equal=self.W_equal, 
				W_plus=self.W_plus, 
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
			if len(detB) == 0: 		# 'N' means empty
				detB.append('N')
			if len(detA) == 0:
				detA.append('N')

		#slow_down(detA, detB, last_detA, last_detB, front_car_laneA, car_done, self.slow_speed, self.safe_dis)
	
			last_detA = detA
			last_detB = detB
			last_laneA_id = laneA_id
			last_laneB_id = laneB_id
			last_laneA_c = laneA_c
			last_laneB_c = laneB_c

		if self.printSteps:
			print(f'simulation end, it takes {step} steps')
		traci.close()
		return step


