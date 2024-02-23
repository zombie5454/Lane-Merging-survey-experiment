from function.scenario import scenario

# 這支程式會跑多次simulation, 然後將結果統計到output.csv裡
# 統計在不同W_plus的大小, 搭配不同演算法產生的結果
# 這支程式需要跑大約3分鐘

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

normal_speed = 14
W_equal=normal_speed * 1
W_plus=normal_speed * 1
numA = 10
numB = 10

f.write(f'numA={numA},numB={numB}\n')

s = scenario()
s.set_numA(10)
s.set_numB(10)

for i in range(11):
	s.set_W_plus(W_plus)
	tot = [0, 0, 0]
	for j in range(3):
		run3(tot, s)
	print('.')
	f.write(f'{W_equal}_{W_plus},')
	tot = list(map(lambda i: str(i/10), tot))	
	f.write(','.join(tot))
	f.write('\n')
	W_plus += normal_speed * 0.2





	
