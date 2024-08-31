import traci
from collections import defaultdict, deque
import sys
from Model.Car import Car, printCars
from Model.Lane_Change import Lane_Change
from Model.Lane_Merging import Lane_Merging
from Util.generateInput import randomDepartTime, randomCar, generateRoute
from Util.action import lane_merge, change_lane_order, slow_down

import pickle


### scenario是用來模擬整體架構的class，其中的run()可以用來跑一次simulation ###

'''
import os, sys

if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:
	sys.exit("please declare environment variable 'SUMO_HOME'")

sys.path.append(os.path.join('c:', os.sep, 'whatever', 'path', 'to', 'sumo', 'tools'))
'''

class Scenario:
	def __init__(self):
		# option, argv
		self.step_length = '0.1'		# sumo/sumo-gui use a time step of one second per default. You may override this using the --step-length <TIME> option. <TIME> is by giving a value in seconds between [0.001 and 1.0].
		self.start_arg = ["sumo", "-c", "Setup/cfg.sumocfg", '--step-length', '0.1', '--no-step-log'] 
		self.lane_change_alg = 'No'
		self.lane_merge_alg = 'FIFO'
		self.new_data = False
		self.printSteps = False		# print出simulation所花的step數
		self.gui = False			# 來讓simulation的過程呈現在內建的GUI上
		self.printInput = False		# print此次ipnut


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
		self.gui = True

	def unset_gui(self):
		self.gui = False

	def set_W_equal(self, w):
		self.W_equal = w

	def set_W_plus(self, w):
		self.W_plus = w

	def set_numA(self, n):
		self.numA = n

	def set_numB(self, n):
		self.numB = n	

	def set_step_length(self, step):
		self.step_length = step

	def set_lane_change_alg(self, name):
		self.lane_change_alg = name

	def set_lane_merge_alg(self, name):
		self.lane_merge_alg = name

	def set_new_data(self):
		self.new_data = True

	def unset_new_data(self):
		self.new_data = False

	def set_printInput(self):
		self.printInput = True

	def unset_printInput(self):
		self.printInput = False


	def run(self):	
	
		#### set start_arg ####
		self.start_arg[4] = self.step_length

		if self.gui:
			self.start_arg[0] = 'sumo-gui'
	
		#### set Cars ####
		departTimeA = []
		departTimeB = []
		if self.new_data:
			departTimeA, departTimeB = randomDepartTime(mingap = self.time_gap, numA=self.numA, numB=self.numB)	
			
		else:		
			# read last simulation's input from input.pickle
			with open('input.pickle', 'rb') as f:
				inputs = pickle.load(f)
				departTimeA = inputs['departTimeA']
				departTimeB = inputs['departTimeB']	
			
		carsA, carsB, merging_num = randomCar(departTimeA, departTimeB)
		generateRoute(carsA, carsB)

		#### set laneChange ####
		laneChange = Lane_Change()
		if self.lane_change_alg.lower() == 'no':
			laneChange.noLaneChange(carsA, carsB, self.lane_change_point, self.normal_speed)
		elif self.lane_change_alg.lower() == 'all':
			laneChange.allLaneChange(carsA, carsB, self.lane_change_point, self.normal_speed)
		elif self.lane_change_alg.lower() == 'nowaiting':
			laneChange.noWaitingLaneChange(carsA, carsB, self.lane_change_point, self.normal_speed, self.time_gap)
		elif self.lane_change_alg.lower() == 'random':
			laneChange.randomLaneChange(carsA, carsB)
		else:
			print('lane_change_alg invalid')
			sys.exit()

		#### set laneMering ####
		lane_merging = Lane_Merging()
		if self.lane_merge_alg.lower() == 'fifo':
			lane_merging.FIFO(laneChange.carsA_after, laneChange.carsB_after)
		elif self.lane_merge_alg.lower() == 'random':
			lane_merging.randomPassingOrder(laneChange.carsA_after, laneChange.carsB_after)
		else:
			print('lane_merge_alg invalid')
			sys.exit()

		#### write input ####

		# write this simulation's input to input.txt
		inputs = {}
		inputs['departTimeA'] = departTimeA
		inputs['departTimeB'] = departTimeB
		inputs['laneA_after_change'] = laneChange.laneA_after_change
		inputs['passing_order'] = lane_merging.passing_order
		with open('input.txt', 'w') as f:
			f.write(str(inputs['departTimeA']) + '\n')
			f.write(str(inputs['departTimeB']) + '\n')
			f.write(str(inputs['laneA_after_change']) + '\n')
			f.write(str(inputs['passing_order']) + '\n')
			f.write('# depart timeA\n# depart timeB\n# laneA_after_change\n# passing_order\n')

		# write this simulation's input to input.pickle
		with open("input.pickle", "wb") as f:
			pickle.dump(inputs, f)

		if self.printInput:
			print("depart timeA: ", departTimeA)
			print("depart timeB: ", departTimeB)
			print("laneA_after_change: ", laneChange.laneA_after_change)
			print("passing_order: ", lane_merging.passing_order)


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
		traci.start(self.start_arg)

		for i, car in enumerate(laneChange.laneA_after_change):
			if car[0] == 'B':
				#print(car)
				traci.vehicle.setRouteID(car, 'rB_c')		# change route of cars in laneB that will lane-change
			if i+1 < len(laneChange.laneA_after_change):
				front_car_laneA[car] = laneChange.laneA_after_change[i+1]
		
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
			tail_has_stop_c, changing_count = change_lane_order(self.safe_dis, front_car_laneA, car_done, laneA_c, laneB_c, laneChange.laneA_after_change, 
				last_laneA_c, last_laneB_c, tail_has_stop_c, laneA_id, changing_count, laneChange.changing_num, self.normal_speed)

			last_passing_step, last_passing_lane, tail_has_stop, merging_count = lane_merge(step=step, 
				passing_order=lane_merging.passing_order,  
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


