import traci

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


def change_lane_order(safe_dis, front_car_laneA, car_done, laneA_c, laneB_c, laneA_after_change, last_laneA_c, last_laneB_c, tail_has_stop_c, laneA_id, changing_count, changing_num, normal_speed):

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
	

def slow_down(detA, detB, last_detA, last_detB, front_car_laneA, car_done, slow_speed, safe_dis):
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