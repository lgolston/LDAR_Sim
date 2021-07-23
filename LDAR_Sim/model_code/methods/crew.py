# ------------------------------------------------------------------------------
# Program:     The LDAR Simulator (LDAR-Sim)
# File:        crew
# Purpose:     Initialize each crew under company
#
# Copyright (C) 2018-2020  Thomas Fox, Mozhou Gao, Thomas Barchyn, Chris Hugenholtz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the MIT License as published
# by the Free Software Foundation, version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# MIT License for more details.

# You should have received a copy of the MIT License
# along with this program.  If not, see <https://opensource.org/licenses/MIT>.
#
# ------------------------------------------------------------------------------

import numpy as np
from importlib import import_module
from aggregator import aggregate


class BaseCrew:
    """
    Base class crew function. Changes made here will affect any inheriting
    classes. To use base class, import and use as argument arguement. ie.

    from methods.crew import crew
    class crew (crew):
        def __init__(self, **kwargs):
            super(crew, self).__init__(**kwargs)
        ...s

    overwrite methods by creating methods in the inheriting class
    after the __init__ function.
    """

    def __init__(self, state, parameters, config, timeseries, deployment_days, id):
        """
        Constructs an individual crew based on defined configuration.
        """
        self.state = state
        self.parameters = parameters
        self.config = config
        self.timeseries = timeseries
        self.deployment_days = deployment_days
        self.id = id
        self.lat = 0
        self.lon = 0
        sched_mod = import_module('methods.deployment.{}_crew'.format(
            self.config['deployment_type'].lower()))
        # Get schedule based on deployment type
        Schedule = getattr(sched_mod, 'Schedule')
        self.schedule = Schedule(self.id, self.lat, self.lon, state,
                                 config, parameters,  deployment_days)

        if self.config['deployment_type'] == 'mobile':
            self.worked_today = False
            self.rollover_sites = []
            self.scheduling = self.config['scheduling']

        return

    def work_a_day(self, site_pool, candidate_flags=None):
        """
        Go to work and find the leaks for a given day
        """
        m_name = self.config['label']
        self.worked_today = False
        self.candidate_flags = candidate_flags
        self.days_skipped = 0
        # Init Schedule method
        self.schedule.start_day()
        
        for sidx, site in enumerate(site_pool):
            if self.state['t'].current_date.hour >= int(self.schedule.end_hour):
                break
            # if there is a site_pool
            if len(site_pool)>0:
                # check the rollover
                if len(self.rollover_sites)>0:
                    # get rollover site 
                    rollover_site = self.rollover_sites[0]
                    # get travel plan to this site 
                    site_plan = self.schedule.plan_visit(rollover_site)
                    if site_plan:
                        self.visit_site(rollover_site)
                        # if this site is finished 
                        if site_plan['remaining_mins'] == 0:
                            # remove the rollover_site
                            self.rollover_sites = []
                        # Update work state
                        self.worked_today = True
                        # Mobile LDAR_mins also includes travel to site time
                        self.schedule.update_schedule(site_plan['LDAR_total_mins'])
                
                # Perform work Day for site pool when time is permitted 
                # a temporary list to store site_plan
                site_plan_list = [] 
                for site in site_pool:
                    site_plan = self.schedule.plan_visit(site)
                    if site_plan:
                        # store site to site_pool_list 
                        site_plan_list.append(site_plan)
                    
                # find next site to visit 
                next_site_plan = self.schedule.choose_site(site_plan_list)
                if next_site_plan:
                    # visit site 
                    self.visit_site(next_site_plan['site'])                    
                    # Update time
                    self.worked_today = True
                    # Mobile LDAR_mins also includes travel to site time
                    self.schedule.update_schedule(next_site_plan['LDAR_total_mins'])
                    
                    # if that site is rollover
                    if next_site_plan['rollover_state']: 
                        self.rollover_sites.append(next_site_plan['site'])
                        self.schedule.choose_accommodation()
                        break
                    # none of site can be accessed today 
                else:
                    # crew need to travel all day to reach the next site  
                    # sort plan list to find the nearest site 
                    sorted_site_plan_list = sorted(site_plan_list,key=lambda k: k['LDAR_total_mins'])
                    if len(sorted_site_plan_list) > 0: 
                        target_site = sorted_site_plan_list[0]['site']
                        # use schedule.choose_accommodation to find the home base 
                        #that nearest to both current location and next site                       
                        self.schedule.choose_accommodation(site=target_site)
                    break
                    
            else:
                self.worked_today = False

        # End day - Update Cost
        if self.worked_today:
            self.schedule.end_day()
            self.timeseries['{}_cost'.format(m_name)][self.state['t'].current_timestep] += \
                self.config['cost_per_day']
            self.timeseries['total_daily_cost'][self.state['t'].current_timestep] += \
                self.config['cost_per_day']

    def visit_site(self, site):
        """
        Look for emissions at the chosen site.
        """
        m_name = self.config['label']

        # Aggregate true emissions to equipment and site level; get list of leaks present
        leaks_present, equipment_rates, site_true_rate = aggregate(
            site, self.state['leaks'])

        # Add vented emissions
        venting = 0
        if self.parameters['consider_venting']:
            venting = self.state['empirical_vents'][
                np.random.randint(0, len(self.state['empirical_vents']))]
        site_true_rate += venting
        for rate in range(len(equipment_rates)):
            equipment_rates[rate] += venting/int(site['equipment_groups'])

        site_detect_results = self.detect_emissions(
            site, leaks_present, equipment_rates, site_true_rate, venting)

        if self.config['measurement_scale'].lower() == 'leak':
            # Remove site from flag pool if leak level measurement
            site['currently_flagged'] = False
        elif site_detect_results:
            # all other sites flag
            self.candidate_flags.append(site_detect_results)

            # Update site
        self.timeseries['{}_sites_visited'.format(
            m_name)][self.state['t'].current_timestep] += 1
        site['{}_surveys_conducted'.format(m_name)] += 1
        site['{}_surveys_done_this_year'.format(m_name)] += 1
        site['{}_t_since_last_LDAR'.format(m_name)] = 0
        # update locations of crews: 
        self.crew_lon = site['lon']
        self.crew_lat = site['lat']
    def detect_emissions(self, *args):
        """ Run module to detect leaks and tag sites
        Returns:
            dict: {
                'site': site,
                'leaks_present': leaks_present,
                'site_true_rate': site_true_rate,
                'site_measured_rate': site_measured_rate,
                'venting': venting
            }
        """
        # Get the type of sensor, and call the the detect emissions function for sensor
        sensor_mod = import_module(
            'methods.sensors.{}'.format(self.config['sensor']))
        detect_emis_sensor = getattr(sensor_mod, 'detect_emissions')
        return detect_emis_sensor(self, *args)
