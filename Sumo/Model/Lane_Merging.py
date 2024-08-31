from Model.Car import Car
import random

# 此為lane merge演算法的class，如果要新增新的演算法，必須要提供(更新)__init__裡的成員變數。
class Lane_Merging:
	def __init__(self) -> None:
		self.passing_order: list[str] = []

	def randomPassingOrder(self, carsA_after: list[Car], carsB_after: list[Car]):
		a = 0
		b = 0
		la = len(carsA_after)
		lb = len(carsB_after)  
		while a < la or b < lb:
			if a >= la and b < lb:
				self.passing_order.append(carsB_after[b].id)
				b += 1
			elif b >= lb and a < la:
				self.passing_order.append(carsA_after[a].id)
				a += 1
			else:
				if random.randint(0,1) == 0:
					self.passing_order.append(carsB_after[b].id)
					b += 1
				else:
					self.passing_order.append(carsA_after[a].id)
					a += 1



	def FIFO(self, carsA_after: list[Car], carsB_after: list[Car]):
		cars: list[Car] = carsA_after + carsB_after
		cars.sort(key=lambda x: x.departTime, reverse=True)
		#printCars(cars)
		for i in cars:
			self.passing_order.append(i.id)