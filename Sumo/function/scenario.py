import traci
from collections import defaultdict, deque
import sys
from function.car import car, printCars
from function.generateInput import randomDepartTime, randomCar, generateRoute
from function.laneChange import randomLaneChange, noLaneChange, allLaneChange, noWaitingLaneChange
from function.passingOrder import randomPassingOrder, FIFO
from function.action import lane_merge, change_lane_order, slow_down

# 這支程式是用來跑simulation
# 如何使用這個程式:
# 	1. 如果要跑一次simulation，記得把,最後一行的run()給他uncommemt掉
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

class scenario:
	def __init__(self):
		# option, argv
		self.step_length = 0.1	# sumo/sumo-gui use a time step of one second per default. You may override this using the --step-length <TIME> option. <TIME> is by giving a value in seconds between [0.001 and 1.0].
		self.start_arg = ["sumo", "-c", "cfg.sumocfg"] 
		self.lane_change_alg = 'No'
		self.lane_merge_alg = 'FIFO'
		self.new_data = False



		# variable
		self.lane_change_point = 250
		self.normal_speed = 14  # 14 m/s = 50.4 km/hr
		self.safe_dis = self.normal_speed * 2
		self.slow_speed = self.normal_speed * 0.6
		self.step_error = self.normal_speed * self.step_length
		self.time_gap = self.safe_dis / self.normal_speed
		self.W_equal = self.normal_speed * 1
		self.W_plus = self.normal_speed * 3
		self.numA = 4
		self.numB = 4



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



	def run(self, arg = sys.argv):	
	
		#### option, argv ####
		step_length = self.step_length	# sumo/sumo-gui use a time step of one second per default. You may override this using the --step-length <TIME> option. <TIME> is by giving a value in seconds between [0.001 and 1.0].
		start_arg = self.start_arg.copy()
		lane_change_alg = self.lane_change_alg
		lane_merge_alg = self.lane_merge_alg
		new_data = self.new_data
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
			#print(inputs)
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
			laneA_after_change, laneB_after_change, changing_num, carsA_after, carsB_after = randomLaneChange(carsA, carsB)    # the order on laneA/laneB after lane-change point
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
		last_laneA_id = ['N'] # 'N' means empty
		last_laneB_id = ['N']
		tail_has_stop = True
		last_laneA_c = ['N']
		last_laneB_c = ['N']
		tail_has_stop_c = True
		front_car_laneA = defaultdict(lambda: 'N')   # save the front car of a car in laneA after lane change
		#print(laneA_after_change)



		#### start stimulation ####
		step = 0
		#print(start_arg)
		traci.start(start_arg)

		for i, car in enumerate(laneA_after_change):
			if car[0] == 'B':
				#print(car)
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

			#change_lane(self.safe_dis, laneA_c, laneB_c, laneA_id, self.lane_change_point, self.step_error)
			tail_has_stop_c, changing_count = change_lane_order(self.safe_dis, front_car_laneA, car_done, laneA_c, laneB_c, laneA_after_change, 
				last_laneA_c, last_laneB_c, tail_has_stop_c, laneA_id, changing_count, changing_num, self.normal_speed)

			last_passing_step, last_passing_lane, tail_has_stop, merging_count = lane_merge(step=step, 
				passing_order=passing_order,   # a pass first, and then a, and then b, ...
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
			if len(detB) == 0: # 'N' means empty
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


		#print(f'simulation end, it takes {step} steps')
		traci.close()
		return step


