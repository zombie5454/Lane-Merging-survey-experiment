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