# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A protocol to calibrate the water system. In addition, to contro the lights.
"""

from pybpodapi.bpod import Bpod
from pybpodapi.state_machine import StateMachine
from pybpodapi.bpod.hardware.events import EventName
from pybpodapi.bpod.hardware.output_channels import OutputChannel
from pybpodapi.com.messaging.trial import Trial
import zaber.serial as zaber_serial
import time

import numpy as np
import json

variables = {
        'ValveOpenTime' : 0.1,
        'Trialnumber_in_block' : 3,
        'LED_ch' : OutputChannel.PWM6,
        'LED_time' : 2,
        'GoCue_ch' : OutputChannel.PWM3,
        'GoCue_time' : 2,
        'Reward_consume_time' : 2,
        'WaterPort_L_ch_out' : 7,
        'WaterPort_L_ch_in' : EventName.Port7In,
        'WaterPort_R_ch_out' : 8,
        'WaterPort_R_ch_in' : EventName.Port8In,
        'iti_base' : 1.,
        'iti_sd' : 0.,
}

my_bpod = Bpod()
print('Variables:', variables)
# ----> Start the task
for triali in range(variables['Trialnumber_in_block']):  # Main loop

    iti_now = np.random.normal(variables['iti_base'],variables['iti_sd'])
    sma = StateMachine(my_bpod)
    sma.add_state(
        state_name='LED_ON',
        state_timer=variables['LED_time'],
        state_change_conditions={EventName.Tup: 'GoCue'},
        output_actions = [(variables['LED_ch'],255)])
    sma.add_state(
	state_name='GoCue',
	state_timer=variables['GoCue_time'],
	state_change_conditions={variables['WaterPort_L_ch_in']: 'Reward_L', variables['WaterPort_R_ch_in']: 'Reward_R', EventName.Tup: 'ITI'},
	output_actions = [(variables['GoCue_ch'],255)])
    sma.add_state(
	state_name='Reward_L',
	state_timer=variables['ValveOpenTime'],
	state_change_conditions={EventName.Tup: 'Consume_reward'},
	output_actions = [('Valve',variables['WaterPort_L_ch_out'])])
    sma.add_state(
	state_name='Reward_R',
	state_timer=variables['ValveOpenTime'],
	state_change_conditions={EventName.Tup: 'Consume_reward'},
	output_actions = [('Valve',variables['WaterPort_R_ch_out'])])
    sma.add_state(
	state_name='Consume_reward',
	state_timer=variables['Reward_consume_time'],
	state_change_conditions={variables['WaterPort_L_ch_in']: 'Consume_reward',variables['WaterPort_R_ch_in']: 'Consume_reward',EventName.Tup: 'ITI'},
	output_actions = [])
    sma.add_state(
	state_name='ITI',
	state_timer=iti_now,
	state_change_conditions={EventName.Tup: 'End'},
	output_actions = [])
    sma.add_state(
        state_name = 'End',
        state_timer = 0,
        state_change_conditions={EventName.Tup: 'exit'},
        output_actions=[])

    my_bpod.send_state_machine(sma)  # Send state machine description to Bpod device

    my_bpod.run_state_machine(sma)  # Run state machine
    print('Trialnumber:', triali + 1)
    print('Trialtype:', 'free choice')

    variables_motor = {
	'LickPort_Lateral_pos' : 'auto',
	'LickPort_RostroCaudal_pos' : 'auto',
    }
    print('LickportMotors:',variables_motor)
    
    #print(my_bpod.session.current_trial)

    #print(my_bpod.workspace_path)
    #datafilename = my_bpod.workspace_path + '\\data.json'
    #with open(datafilename, 'w') as outfile:
	#    json.dump(my_bpod.session.current_trial, outfile)




my_bpod.close()

