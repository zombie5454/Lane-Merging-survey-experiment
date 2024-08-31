from Model.Scenario import Scenario 
import sys

######### 此程式用來簡單示範如何跑一次simulation ###########

scenario = Scenario()
arg = sys.argv

#### argv #####
for i in range(1, len(arg)):
    if arg[i] == '--step-length' or arg[i] == '--sl':
        scenario.set_step_length(arg[i+1])
    if arg[i] == '-c':
        scenario.set_lane_change_alg(arg[i+1])
    if arg[i] == '-m':
        scenario.set_lane_merge_alg(arg[i+1])
    if arg[i] == '--new':               # 使用新input
        scenario.set_new_data()
    if arg[i] == '--gui':               # 顯示GUI
        scenario.set_gui()
    if arg[i] == '--show-input':        # print出input
        scenario.set_printInput()                    

scenario.set_printSteps()
scenario.run()					



