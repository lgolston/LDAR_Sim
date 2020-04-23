#------------------------------------------------------------------------------
# Program:     The LDAR Simulator (LDAR-Sim) 
# File:        Operator
# Purpose:     Initialize and manage operator detection module
#
# Copyright (C) 2019  Thomas Fox, Mozhou Gao, Thomas Barchyn, Chris Hugenholtz
#    
# This file is for peer review. Do not distribute or modify it in any way.
# This program is presented WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#------------------------------------------------------------------------------

import numpy as np

class operator_agent:
    def __init__ (self, timeseries, parameters, state):
        '''
        Constructs an operator who visits all sites and occasionally finds
        a leak.
        '''
        print('Initializing operator...')
        self.parameters = parameters
        self.state = state
        self.timeseries = timeseries
        self.init_mean_leaks = np.mean(self.state['init_leaks'])
        self.init_sum_leaks = np.sum(self.state['init_leaks']) 
        self.n_sites = len(self.state['sites'])
        self.timeseries['operator_redund_tags'] = np.zeros(self.parameters['timesteps'])
        self.timeseries['operator_tags'] = np.zeros(self.parameters['timesteps'])

        return
 
    def work_a_day (self):
        '''
        Detect leaks during operator visits. 
        Detection can be a function of leak-size.
        '''      
        
        active_leaks = self.timeseries['active_leaks'][self.state['t'].current_timestep]
        leak_term = ( self.init_sum_leaks / active_leaks ) * self.init_mean_leaks
        
        for leak in self.state['leaks']:
            if leak['status'] == 'active':
                prob_detect = self.parameters['LPR'] * 7 / leak_term    
                prob_detect += self.parameters['max_det_op'] * (leak['rate']/self.state['max_rate'])
                if prob_detect > 1:
                    prob_detect = 1
                prob_detect = prob_detect * self.parameters['operator_strength']
                detect = np.random.binomial(1, prob_detect)

                if detect == True:
                    if leak['tagged'] == True:
                        self.timeseries['operator_redund_tags'][self.state['t'].current_timestep] += 1
                        
                    elif leak['tagged'] == False:
                        # Add these leaks to the 'tag pool'
                        leak['tagged'] = True
                        leak['date_found'] = self.state['t'].current_date
                        leak['found_by_company'] = 'operator'
                        leak['found_by_crew'] = 1
                        self.state['tags'].append(leak)
                        self.timeseries['operator_tags'][self.state['t'].current_timestep] += 1
                        
        return
    