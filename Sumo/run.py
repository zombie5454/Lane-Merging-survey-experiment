from function.scenario import scenario 
import sys

######### 此程式用來簡單示範如何跑一次simulation ###########

s = scenario()
s.set_printSteps() 					# print出simulation所花的step數
#s.set_gui()                         # 顯示GUI

### argument可以用argv的方式傳，也可以直接修改程式碼 ###
s.run(arg=sys.argv)					
#s.run(arg=['', --c', 'all'])			