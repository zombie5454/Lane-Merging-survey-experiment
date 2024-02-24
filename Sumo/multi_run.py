from function.scenario import scenario
import csv

# 這支程式會跑多次simulation, 然後將結果統計到output.csv裡
# 統計在不同W_plus的大小, 搭配不同演算法產生的結果
# 這支程式需要跑大約3分鐘

def run3(tot, s):
	tot[0] += s.run(arg=['', 'new'])
	tot[1] += s.run(arg=['', '--c', 'all'])
	tot[2] += s.run(arg=['', '--c', 'nowaiting'])
	return 



s = scenario()

normal_speed = s.normal_speed
W_equal=normal_speed * 1
W_plus=normal_speed * 1
numA = 10
numB = 10
s.set_numA(numA)
s.set_numB(numB)



with open('output.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow([f'numA={s.numA}', f'numB={s.numB}'])
	writer.writerow(['W=', 'W+', 'noChange', 'allChange', 'noWaiting'])
	
	for i in range(11):
		s.set_W_plus(W_plus)
		tot = [0, 0, 0]
		for j in range(3):
			run3(tot, s)
		print('.')
		tot = list(map(lambda i: str(i/10), tot))	
		writer.writerow([f'{W_equal}', f'{W_plus}'] + tot)
		W_plus += normal_speed * 0.2





	
