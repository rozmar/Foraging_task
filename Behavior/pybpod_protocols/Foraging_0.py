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


variables = {
        'ValveOpenTime' : 0.035,
        'Trialnumber_in_block' : 15,
        'reward_probabilities_R' : [1,1,0,1],
        'reward_probabilities_L' : [1,0,1,0],
        'baseline_time' : 1,
        'GoCue_ch' : OutputChannel.PWM3,
        'GoCue_time' : 2,
        'Reward_consume_time' : 2,
        'WaterPort_L_ch_out' : 7,
        'WaterPort_L_ch_in' : EventName.Port7In,
        'WaterPort_R_ch_out' : 8,
        'WaterPort_R_ch_in' : EventName.Port8In,
        'Choice_cue_L_ch' : OutputChannel.PWM4,
        'Choice_cue_R_ch' : OutputChannel.PWM5,
        'iti_base' : 2.,
        'iti_min' : 1.,
        'iti_sd' : 1.,
        'comport_motor' : 'COM7',
        'motor_retractiondistance' : 40000,
        'motor_retract_waterport' : True,
}

# soft codes : 1 - retract RC motor; 2 - protract RC motor
def my_softcode_handler(data):
    print(data)
    if data == 1:
        positiontomove = variables['motor_retractedposition']
        print("retracting ZaberMotor")
    elif data == 2:
        print("protracting Zabermotor")
        positiontomove = variables['motor_forwardposition']
    for zabertry_i in range(0,100): # when the COMport is occupied, it will try again
        try:
            with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
                moveabs_cmd = zaber_serial.BinaryCommand(1,20,positiontomove)
                ser.write(moveabs_cmd)
                break
        except:
            print('can''t access Zaber ' + str(zabertry_i))
            

def read_motor_position(comport):
    for zabertry_i in range(0,100): # when the COMport is occupied, it will try again
        try:
            with zaber_serial.BinarySerial(comport) as ser:
                Forward_Backward_device = zaber_serial.BinaryDevice(ser,1)
                Left_Right_device = zaber_serial.BinaryDevice(ser,2)
                pos_Forward_Backward = Forward_Backward_device.get_position()
                pos_Left_Right = Left_Right_device.get_position()
                variables_motor = {
            	'LickPort_Lateral_pos' : pos_Left_Right,
            	'LickPort_RostroCaudal_pos' : pos_Forward_Backward,
                }
                return variables_motor                
                break
        except:
            print('can''t access Zaber ' + str(zabertry_i))



variables_motor = read_motor_position(variables['comport_motor'])
variables['motor_forwardposition'] = variables_motor['LickPort_RostroCaudal_pos']
variables['motor_retractedposition'] = variables_motor['LickPort_RostroCaudal_pos'] + variables['motor_retractiondistance']




my_bpod = Bpod()
my_bpod.softcode_handler_function = my_softcode_handler
print('Variables:', variables)
# ----> Start the task
for blocki , p_R , p_L in enumerate(variables['reward_probabilities_R'], variables['reward_probabilities_L']):
    for triali in range(variables['Trialnumber_in_block']):  # Main loop
        reward_L = np.random.uniform(0.,1.) < p_L
        reward_R = np.random.uniform(0.,1.) < p_R
        iti_now = np.random.normal(variables['iti_base'],variables['iti_sd'])
        if iti_now < variables['iti_min']:
            iti_now = variables['iti_min']           
        sma = StateMachine(my_bpod)
        sma.add_state(
            state_name='Start',
            state_timer=variables['baseline_time'],
            state_change_conditions={EventName.Tup: 'GoCue'},
            output_actions = [])
        sma.add_state(
        	state_name='GoCue',
        	state_timer=variables['GoCue_time'],
        	state_change_conditions={variables['WaterPort_L_ch_in']: 'Choice_L', variables['WaterPort_R_ch_in']: 'Choice_R', EventName.Tup: 'ITI'},
        	output_actions = [(variables['GoCue_ch'],255)])
        if reward_L:
            sma.add_state(
            	state_name='Choice_L',
            	state_timer=0,
            	state_change_conditions={EventName.Tup: 'Reward_L'},
            	output_actions = [(variables['Choice_cue_L_ch'],255)])
        else:
            sma.add_state(
            	state_name='Choice_L',
            	state_timer=0,
            	state_change_conditions={EventName.Tup: 'NO_Reward'},
            	output_actions = [(variables['Choice_cue_L_ch'],255)])
        if reward_R:
            sma.add_state(
            	state_name='Choice_R',
            	state_timer=0,
            	state_change_conditions={EventName.Tup: 'Reward_R'},
            	output_actions = [(variables['Choice_cue_R_ch'],255)])
        else:
            sma.add_state(
            	state_name='Choice_R',
            	state_timer=0,
            	state_change_conditions={EventName.Tup: 'NO_Reward'},
            	output_actions = [(variables['Choice_cue_R_ch'],255)])
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
        	state_name='NO_Reward',
        	state_timer=0,
        	state_change_conditions={EventName.Tup: 'ITI'},
        	output_actions = [])
        sma.add_state(
        	state_name='Consume_reward',
        	state_timer=variables['Reward_consume_time'],
        	state_change_conditions={variables['WaterPort_L_ch_in']: 'Consume_reward_return',variables['WaterPort_R_ch_in']: 'Consume_reward_return',EventName.Tup: 'ITI'},
        	output_actions = [])
        sma.add_state(
        	state_name='Consume_reward_return',
        	state_timer=.1,
        	state_change_conditions={EventName.Tup: 'Consume_reward'},
        	output_actions = [])
        if variables['motor_retract_waterport']:
            sma.add_state(
            	state_name='ITI',
            	state_timer=iti_now,
            	state_change_conditions={EventName.Tup: 'End'},
            	output_actions = [(Bpod.OutputChannels.SoftCode, 1)])
            sma.add_state(
                state_name = 'End',
                state_timer = 0,
                state_change_conditions={EventName.Tup: 'exit'},
                output_actions=[(Bpod.OutputChannels.SoftCode, 2)])
        else:    
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
        print('Blocknumber:', blocki + 1)
        print('Trialnumber:', triali + 1)
        print('Trialtype:', 'free choice')
        
        variables_motor = read_motor_position(variables['comport_motor'])
        
        print('LickportMotors:',variables_motor)
    
        #print(my_bpod.session.current_trial)
    
        #print(my_bpod.workspace_path)
        #datafilename = my_bpod.workspace_path + '\\data.json'
        #with open(datafilename, 'w') as outfile:
    	#    json.dump(my_bpod.session.current_trial, outfile)
    
    
    
    
    my_bpod.close()

