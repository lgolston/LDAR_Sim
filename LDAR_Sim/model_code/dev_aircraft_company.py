from methods.company import BaseCompany
from methods.crew import BaseCrew


class dev_aircraft_company(BaseCompany):
    """ Test aircraft company module. Company managing fixed agents.
        Inherits base method base class company
    """

    def __init__(self, state, parameters, config, timeseries):
        super(dev_aircraft_company, self).__init__(state, parameters, config, timeseries)
        # --- Custom Init ---
        # -------------------
        # Initiate Crews - This is done outside of base class

    # --- Custom Methods ---
    # ----------------------


class Crew(BaseCrew):
    """ Test Company module. Initialize each crew for company.
        Inherits base method base class company
    """

    def __init__(self, state, parameters, config, timeseries, deployment_days, id):
        super(Crew, self).__init__(state, parameters, config, timeseries, deployment_days, id)
        # --- Custom Init ---
        # -------------------

    # --- Custom Methods ---
    # ----------------------
