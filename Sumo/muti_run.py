from run3 import *
# 這支程式是用來跑多次simulation然後統計到output.csv裡
# 如何使用這個程式
#	1. 記得把run3.py第441行的start_arg = ["sumo-gui", "-c", "cfg.sumocfg"]中的"sumo-gui"改成"sumo"
#	2. 記得把run3.py第627行(print(f'simulation end, it takes {step} steps'))給他commemt掉
#	3. 記得把run3.py最後一行的run()給他commemt掉
#	4. 跑python3 muti_run.py


def run3(tot, Wequal = normal_speed * 1, Wplus = normal_speed * 2, numA=4, numB=4):
	tot[0] += run(arg=['', 'new'], Wequal=Wequal, Wplus=Wplus, numA=numA, numB=numB)
	tot[1] += run(arg=['', '--c', 'all'], Wequal=Wequal, Wplus=Wplus, numA=numA, numB=numB)
	tot[2] += run(arg=['', '--c', 'nowaiting'], Wequal=Wequal, Wplus=Wplus, numA=numA, numB=numB)
	return 

f = open('output.csv', 'w')
f.write('')
f.close()

f = open('output.csv', 'a')
f.write('W=_W+,noChange,allChange,noWaiting\n')
'''
Wequal=normal_speed * 1
Wplus=normal_speed * 1
numA = 4
numB = 4
f.write(f'numA={numA},numB={numB}\n')

for i in range(11):
	tot = [0, 0, 0]
	for j in range(10):
		run3(tot, Wequal=Wequal, Wplus=Wplus)
		print('.')
	f.write(f'{Wequal}_{Wplus},')
	tot = list(map(lambda i: str(i/10), tot))	
		#print(out)
	f.write(','.join(tot))
	f.write('\n')
	Wplus += normal_speed * 0.2
'''
Wequal=normal_speed * 1
Wplus=normal_speed * 1

numA = 10
numB = 10
f.write(f'numA={numA},numB={numB}\n')

for i in range(11):
	tot = [0, 0, 0]
	for j in range(10):
		run3(tot, Wequal=Wequal, Wplus=Wplus, numA=numA, numB=numB)
		print('.')
	f.write(f'{Wequal}_{Wplus},')
	tot = list(map(lambda i: str(i/10), tot))	
		#print(out)
	f.write(','.join(tot))
	f.write('\n')
	Wplus += normal_speed * 0.2





	
