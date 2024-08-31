from Model.Car import Car
import random

# 此為lane change演算法的class，如果要新增新的演算法，必須要提供(更新)__init__裡的成員變數。
class Lane_Change:
    def __init__(self) -> None:
        self.laneA_after_change: list[str] = []
        self.laneB_after_change: list[str] = []
        self.changing_num = -1
        self.carsA_after: list[Car] = []
        self.carsB_after: list[Car] = []

    def noLaneChange(self, carsA: list[Car], carsB: list[Car], lane_change_point, normal_speed):
        for i in range(len(carsA)-1, -1, -1):
            carsA[i].passChangeTime = lane_change_point / normal_speed + carsA[i].departTime
            self.laneA_after_change.append(carsA[i].id)
            self.carsA_after.append(carsA[i])
        for i in range(len(carsB)-1, -1, -1):
            carsB[i].passChangeTime = lane_change_point / normal_speed + carsB[i].departTime
            self.laneB_after_change.append(carsB[i].id)
            self.carsB_after.append(carsB[i])

        self.changing_num = 0

    def allLaneChange(self, carsA: list[Car], carsB: list[Car], lane_change_point, normal_speed):
        cars: list[Car] = carsA + carsB
        cars.sort(key=lambda x: x.departTime, reverse=True)
        for car in cars:
            car.passChangeTime = lane_change_point / normal_speed + car.departTime
            self.laneA_after_change.append(car.id)
            self.carsA_after.append(car)

        self.changing_num = len(carsB)

    def noWaitingLaneChange(self, carsA: list[Car], carsB: list[Car], lane_change_point, normal_speed, time_gap = 1):
        cars: list[Car] = carsA + carsB
        cars.sort(key=lambda x: x.departTime, reverse=True)
        for i in range(len(cars)):
            if cars[i].id[0] == 'A':
                self.laneA_after_change.append(cars[i].id)
                self.carsA_after.append(cars[i])
            else:
                front_gap = 1000000
                back_gap = 1000000
                if i+1 < len(cars):
                    front_gap = cars[i].departTime - cars[i+1].departTime
                if i-1 >= 0:
                    back_gap = cars[i-1].departTime - cars[i].departTime
                if front_gap >= time_gap and back_gap >= time_gap:
                    self.laneA_after_change.append(cars[i].id)
                    self.carsA_after.append(cars[i])
                else:
                    self.laneB_after_change.append(cars[i].id)
                    self.carsB_after.append(cars[i])


            cars[i].passChangeTime = lane_change_point / normal_speed + cars[i].departTime

        self.changing_num = len(carsB)-len(self.laneB_after_change)

    def randomLaneChange(self, carsA: list[Car], carsB: list[Car]):
        a = len(carsA)-1
        b = len(carsB)-1
        while a >= 0 or b >= 0:
            if a < 0 and b >= 0:
                if random.randint(0,1) == 0:
                    self.laneA_after_change.append(carsB[b].id)
                    self.carsA_after.append(carsB[b])
                else:
                    self.laneB_after_change.append(carsB[b].id)
                    self.carsB_after.append(carsB[b])
                b -= 1
            elif b < 0 and a >= 0:
                self.laneA_after_change.append(carsA[a].id)  
                self.carsA_after.append(carsA[a])   
                a -= 1
            else:
                if random.randint(0,1) == 0:
                    if random.randint(0,1) == 0:
                        self.laneA_after_change.append(carsB[b].id) 
                        self.carsA_after.append(carsB[b]) 
                    else: 
                        self.laneB_after_change.append(carsB[b].id)
                        self.carsB_after.append(carsB[b])
                    b -= 1
                else:
                    self.laneA_after_change.append(carsA[a].id)
                    self.carsA_after.append(carsA[a])
                    a -= 1

        self.changing_num = len(carsB) - len(self.laneB_after_change)

