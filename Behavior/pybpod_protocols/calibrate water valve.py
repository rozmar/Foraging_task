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

Dropnum = 1
ValveOpenTime = 0.03#nds

ValveOpenTime_L = 0.03#nds
ValveCloseTime = .2

my_bpod = Bpod()


# ----> Start the task

for i in range(Dropnum):  # Main loop

    print('Trial: ', i + 1)

    sma = StateMachine(my_bpod)

    sma.add_state(
        state_name='Open Valves',
        state_timer=ValveOpenTime,
        state_change_conditions={EventName.Tup: 'Close Valves'},
        output_actions = [('Valve',7), ('Valve',8), (OutputChannel.PWM3, 255)])
    sma.add_state(
        state_name = 'Close Valves',
        state_timer = ValveCloseTime,
        state_change_conditions={EventName.Tup: 'exit'},
        output_actions=[])

    my_bpod.send_state_machine(sma)  # Send state machine description to Bpod device
    my_bpod.run_state_machine(sma)  # Run state machine


my_bpod.close()



