from function.scenario import scenario
# 這支程式是用來跑多次simulation然後統計到output.csv裡
# 如何使用這個程式
#	1. 記得把run3.py第441行的start_arg = ["sumo-gui", "-c", "cfg.sumocfg"]中的"sumo-gui"改成"sumo"
#	2. 記得把run3.py第627行(print(f'simulation end, it takes {step} steps'))給他commemt掉
#	3. 記得把run3.py最後一行的run()給他commemt掉
#	4. 跑python3 muti_run.py


def run3(tot, s):
	tot[0] += s.run(arg=['', 'new'])
	tot[1] += s.run(arg=['', '--c', 'all'])
	tot[2] += s.run(arg=['', '--c', 'nowaiting'])
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

normal_speed = 14
Wequal=normal_speed * 1
Wplus=normal_speed * 1
numA = 10
numB = 10

f.write(f'numA={numA},numB={numB}\n')


s = scenario()
s.set_numA(10)
s.set_numB(10)

for i in range(11):
	s.set_W_plus(Wplus)
	tot = [0, 0, 0]
	for j in range(3):
		run3(tot, s)
		print('.')
	f.write(f'{Wequal}_{Wplus},')
	tot = list(map(lambda i: str(i/10), tot))	
		#print(out)
	f.write(','.join(tot))
	f.write('\n')
	Wplus += normal_speed * 0.2





	
