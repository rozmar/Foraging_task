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


reward_ratio_pairs=[[.4,.05],[.3857,.0643],[.3375,.1125],[.225,.225]]
blocknum = 7 # number of blocks
p_reward_L=[.225] # the first block is set to 50% reward rate
p_reward_R=[.225] # the first block is set to 50% reward rate
for i in range(blocknum): # reward rate pairs are chosen randomly
    ratiopairidx=np.random.choice(range(len(reward_ratio_pairs)))
    reward_ratio_pair=reward_ratio_pairs[ratiopairidx]
    np.random.shuffle(reward_ratio_pair)
    p_reward_L.append(reward_ratio_pair[0])
    p_reward_R.append(reward_ratio_pair[1])

variables = {
        'ValveOpenTime_L' : .04,#0.05,#
        'ValveOpenTime_R' : .03,#0.06,#
        'Trialnumber_in_block' : 5,
        'reward_probabilities_R' : [1,0,1],#,[.7,.3,.6,.4,.5],#[.7,.8,.2,.7,.3,.6,.4,.5],#[1,.9,0,.8,0,.7,0], #p_reward_R,#[.7,.6,,]
        'reward_probabilities_L' : [1,1,0],#[.3,.7,.4,.6,.5], #[.7,.2,.8,.3,.7,.4,.6,.5], #[1,0,.9,0,.8,0,.7],#p_reward_L,#[.7,0,.7,0,.6,0,.5], #[.4,.1,,]
        'baseline_time' : 1, # time needed for mouse not to lick before GO cue
        'baseline_time_min' : .5, # minimum value
        'baseline_time_sd' : 1, # randomization parameter
        'GoCue_ch' : OutputChannel.PWM5,
        'GoCue_time' : 2, # time for the mouse to lick
        'Reward_consume_time' : 1, # time needed without lick  to go to the next trial
        'WaterPort_L_ch_out' : 7,
        'WaterPort_L_ch_in' : EventName.Port7In,
        'WaterPort_R_ch_out' : 8,
        'WaterPort_R_ch_in' : EventName.Port8In,
        'Choice_cue_L_ch' : OutputChannel.PWM7,
        'Choice_cue_R_ch' : OutputChannel.PWM8,
        'iti_base' : 2., 
        'iti_min' : 1., # minimum ITI
        'iti_sd' : 1., # randomization parameter
        'comport_motor' : 'COM7',
        'motor_retractiondistance' : 80000,
        'motor_retract_waterport' : True,
        'accumulate_reward': True,
        'auto_water': True,
        'auto_water_time_multiplier': 0.5,
        'early_lick_punishment': True,
}
reward_L_accumulated = False

reward_R_accumulated = False
# soft codes : 1 - retract RC motor; 2 - protract RC motor

def my_softcode_handler(data):
    print(data)
    if data == 1:
        positiontomove = variables['motor_retractedposition']
        print("retracting ZaberMotor")
        retract_protract_motor(positiontomove)
    elif data == 2:
        positiontomove = variables['motor_forwardposition']
        print("protracting Zabermotor")
        retract_protract_motor(positiontomove)
def retract_protract_motor(positiontomove):
    for zabertry_i in range(0,1000): # when the COMport is occupied, it will try again
        try:
            with zaber_serial.BinarySerial(variables['comport_motor']) as ser:
                moveabs_cmd = zaber_serial.BinaryCommand(1,20,positiontomove)
                ser.write(moveabs_cmd)
                break
        except zaber_serial.binaryserial.serial.SerialException:
            print('can''t access Zaber ' + str(zabertry_i))
            time.sleep(.01)
def read_motor_position(comport):
    for zabertry_i in range(0,1000): # when the COMport is occupied, it will try again
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
        except zaber_serial.binaryserial.serial.SerialException:
            print('can''t access Zaber ' + str(zabertry_i))
            time.sleep(.01)


variables_motor = read_motor_position(variables['comport_motor'])
variables['motor_forwardposition'] = variables_motor['LickPort_RostroCaudal_pos']
variables['motor_retractedposition'] = variables_motor['LickPort_RostroCaudal_pos'] + variables['motor_retractiondistance']

my_bpod = Bpod()
my_bpod.softcode_handler_function = my_softcode_handler

print('Variables:', variables)

# ----> Start the task
for blocki , (p_R , p_L) in enumerate(zip(variables['reward_probabilities_R'], variables['reward_probabilities_L'])):
    for triali in range(variables['Trialnumber_in_block']):  # Main loop
        reward_L = np.random.uniform(0.,1.) < p_L
        reward_R = np.random.uniform(0.,1.) < p_R
        iti_now = np.random.normal(variables['iti_base'],variables['iti_sd'])
        if iti_now < variables['iti_min']:
            iti_now = variables['iti_min']    
        baselinetime_now = np.random.normal(variables['baseline_time'],variables['baseline_time_sd'])
        if baselinetime_now < variables['baseline_time_min']:
            baselinetime_now = variables['baseline_time_min']   
        sma = StateMachine(my_bpod)
        if variables['early_lick_punishment']:
            sma.add_state(
                state_name='Start',
                state_timer=baselinetime_now,
                state_change_conditions={variables['WaterPort_L_ch_in']: 'BackToBaseline', variables['WaterPort_R_ch_in']: 'BackToBaseline',EventName.Tup: 'GoCue'},
                output_actions = [])
        else:
            sma.add_state(
                state_name='Start',
                state_timer=baselinetime_now,
                state_change_conditions={EventName.Tup: 'GoCue'},
                output_actions = [])
        sma.add_state(
        	state_name='BackToBaseline',
        	state_timer=0.001,
        	state_change_conditions={EventName.Tup: 'Start'},
        	output_actions = [])
        # autowater comes here!!
        if variables['auto_water']:
            sma.add_state(
            	state_name='GoCue',
            	state_timer=0,
            	state_change_conditions={EventName.Tup: 'Auto_Water_L'},
            	output_actions = [])
            if reward_L or reward_L_accumulated:
                sma.add_state(
                	state_name='Auto_Water_L',
                	state_timer=variables['ValveOpenTime_L']*variables['auto_water_time_multiplier'],
                	state_change_conditions={EventName.Tup: 'Auto_Water_R'},
                	output_actions = [('Valve',variables['WaterPort_L_ch_out'])])
            else:
                sma.add_state(
                	state_name='Auto_Water_L',
                	state_timer=0,
                	state_change_conditions={EventName.Tup: 'Auto_Water_R'},
                	output_actions = [])
            if reward_R or reward_R_accumulated:
                sma.add_state(
                	state_name='Auto_Water_R',
                	state_timer=variables['ValveOpenTime_R']*variables['auto_water_time_multiplier'],
                	state_change_conditions={EventName.Tup: 'GoCue_real'},
                	output_actions = [('Valve',variables['WaterPort_R_ch_out'])])
            else:
                sma.add_state(
                	state_name='Auto_Water_R',
                	state_timer=0,
                	state_change_conditions={EventName.Tup: 'GoCue_real'},
                	output_actions = [])
            sma.add_state(
            	state_name='GoCue_real',
            	state_timer=variables['GoCue_time'],
            	state_change_conditions={variables['WaterPort_L_ch_in']: 'Choice_L', variables['WaterPort_R_ch_in']: 'Choice_R', EventName.Tup: 'ITI'},
            	output_actions = [(variables['GoCue_ch'],255)])
        else:
            sma.add_state(
            	state_name='GoCue',
            	state_timer=variables['GoCue_time'],
            	state_change_conditions={variables['WaterPort_L_ch_in']: 'Choice_L', variables['WaterPort_R_ch_in']: 'Choice_R', EventName.Tup: 'ITI'},
            	output_actions = [(variables['GoCue_ch'],255)])
        if reward_L or reward_L_accumulated:
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
        if reward_R or reward_R_accumulated:
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
        	state_timer=variables['ValveOpenTime_L'],
        	state_change_conditions={EventName.Tup: 'Consume_reward'},
        	output_actions = [('Valve',variables['WaterPort_L_ch_out'])])
        sma.add_state(
        	state_name='Reward_R',
        	state_timer=variables['ValveOpenTime_R'],
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
        
        trialdata = my_bpod.session.current_trial.export()
        reward_L_consumed = not np.isnan(trialdata['States timestamps']['Reward_L'][0][0])
        reward_R_consumed = not np.isnan(trialdata['States timestamps']['Reward_R'][0][0])
        
        if variables['accumulate_reward']:
            if reward_L_consumed:
                reward_L_accumulated = False
            elif reward_L and not reward_L_consumed:
                reward_L_accumulated = True
            if reward_R_consumed:
                reward_R_accumulated = False
            elif reward_R and not reward_R_consumed:
                reward_R_accumulated = True
        
        print('Blocknumber:', blocki + 1)
        print('Trialnumber:', triali + 1)
        print('Trialtype:', 'free choice')
        print('reward_L_accumulated:',reward_L_accumulated)
        print('reward_R_accumulated:',reward_R_accumulated)
        
        variables_motor = read_motor_position(variables['comport_motor'])
        
        print('LickportMotors:',variables_motor)
           
    
    
my_bpod.close()

