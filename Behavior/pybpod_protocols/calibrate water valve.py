# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A protocol to calibrate the water system. In addition, to contro the lights.
"""

from pybpodapi.bpod import Bpod
from pybpodapi.state_machine import StateMachine
from pybpodapi.bpod.hardware.events import EventName
from pybpodapi.bpod.hardware.output_channels import OutputChannel
import timeit

valvetimes = [.025,.03,.035]
Dropnum = 5
ValveOpenTime_L = 0.1#ds
ValveOpenTime_R = 0.1#nds
ValveCloseTime = 3

my_bpod = Bpod()


# ----> Start the task
for valvetime in valvetimes:
    ValveOpenTime_L = valvetime
    ValveOpenTime_R = valvetime
    print(ValveOpenTime_R)
    for i in range(Dropnum):  # Main loop
	    print('Trial: ', i + 1)

	    sma = StateMachine(my_bpod)
	    sma.add_state(
		state_name = 'Wait',
		state_timer = 100,
		state_change_conditions={EventName.Port7In:'Open Left',EventName.Port8In:'Open Left',EventName.Tup: 'exit'},
		output_actions=[])
	    sma.add_state(
		state_name='Open Left',
		state_timer=ValveOpenTime_L,
		state_change_conditions={EventName.Tup: 'Open Right'},
		output_actions = [('Valve',7)])
	    sma.add_state(
		state_name='Open Right',
		state_timer=ValveOpenTime_R,
		state_change_conditions={EventName.Tup: 'Close Valves'},
		output_actions = [('Valve',8)])
	    if i == 0:
		    sma.add_state(
			state_name = 'Close Valves',
			state_timer = ValveCloseTime,
			state_change_conditions={EventName.Tup: 'exit'},
			output_actions=[(OutputChannel.PWM3, 255)])

	    else:
		    sma.add_state(
			state_name = 'Close Valves',
			state_timer = ValveCloseTime,
			state_change_conditions={EventName.Tup: 'exit'},
			output_actions=[])

	    my_bpod.send_state_machine(sma)  # Send state machine description to Bpod device
	    my_bpod.run_state_machine(sma)  # Run state machine


my_bpod.close()



