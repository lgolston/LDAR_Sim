from methods.fixed_company import fixed_company
from methods.fixed_crew import fixed_crew


class dev_fixed_company(fixed_company):
    """ Dev Company module. Company managing fixed agents.
        Inherits base method base class company
    """

    def __init__(self, state, parameters, config, timeseries):
        super(dev_fixed_company, self).__init__(state, parameters, config, timeseries)
        # --- Custom Init ---
        # -------------------
        # Initiate Crews - This is done outside of base class
        # Initialize the individual fixed crews (the agents) - each is a single fixed sensor
        m_name = self.config['name']
        for site in self.state['sites']:
            n_fixed = int(site['fixed_sensors'])
            for i in range(n_fixed):
                self.crews.append(
                    fixed_crew(
                        state, parameters, config, timeseries, site, self.deployment_days,
                        id=site['facility_ID'] + '-' + str(i + 1)))
                self.timeseries['{}_cost'.format(m_name)][self.state['t'].current_timestep] += \
                    self.config['up_front_cost']

    # --- Custom Methods ---
    # ----------------------


class crew(fixed_crew):
    """ Test Company module. Initialize each crew for company.
        Inherits base method base class company
    """

    def __init__(self, state, parameters, config, timeseries, deployment_days, id):
        super(crew, self).__init__(state, parameters, config, timeseries, deployment_days, id)
        # --- Custom Init ---
        # -------------------

    # --- Custom Methods ---
    # ----------------------
