"""
An alternative sensor, specifically built to replicate the probability of detection
    curves provided by a METEC report, which factor in wind speeds
"""
# ------------------------------------------------------------------------------
# Program:     The LDAR Simulator (LDAR-Sim)
# File:        external_sensors.METEC_WIND
# Purpose:     METEC specific deployment classes and methods based on variable wind
#
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
from methods.funcs import measured_rate
from utils.attribution import update_tag
from utils.unit_converter import gas_convert

# Constants
# g/s to kg/hr conversion factor
GsTOKGh = 3.6
# m/s to km/hr conversion factor
MsTOKMh = 3.6


def detect_emissions(
    self,
    site,
    covered_leaks,
    covered_equipment_rates,
    covered_site_rate,
    site_rate,
    venting,
    equipment_rates,
):
    """
    An alternative sensor module, specifically built to replicate the probability of detection
    curve of technology whose detection capabilities are reflective of a METEC wind dependent
    probability of detection curve.

    Utilizes 3 values set as the MDL:
        mdl = [a, b, c]
        where
        a and b : are the PoD curve variables
        c : represents the floor/minimum cutoff value of the leak rates that the sensor can detect.
        The cutoff value will be compared to a non-wind normalized rate.

    PoD = 1 / (1 + e ^ (a - b * r ))

    a = first MDL value
    b = second MDL value
    r = emission rate normalized by wind speed

    Args:
        site (site obj): Site in which crew is working at
        covered_leaks (list): list of leak objects that can be detected by the crew
        covered_equipment_rates (list): list of equipment leak rates that can be
                                        detected by the crew
        covered_site_rate (float): total site emissions from leaks that are observable
                                    from a crew
        site_rate (float): total site emissions from leaks all leaks at site
        venting (float): total site emissions from venting
        equipment_rates (list): list of equipment leak rates for each equipment group

    Returns:
        site report (dict):
                site  (site obj): same as input
                leaks_present (list): same as covered leaks input
                site_true_rate (float): same as site_rate
                site_measured_rate (float): total emis from all leaks measured
                equip_measured_rates (list): total of all leaks measured for each equip group
                venting (float): same as input
                found_leak (boolean): Did the crew find at least one leak at the site
    """
    missed_leaks_str = "{}_missed_leaks".format(self.config["label"])
    equip_measured_rates = []
    site_measured_rate = 0
    found_leak = False
    n_leaks = len(covered_leaks)
    mdl = self.config["sensor"]["MDL"]

    hourly_windspeed = self.state["weather"].get_hourly_weather(
        ["winds"], self.state["t"].current_date, number_of_hours=1, site=site
    )
    average_wind = np.average(hourly_windspeed["winds"])

    if self.config["measurement_scale"] == "site":
        # Calculate the rate per wind based on the overall site rate
        rate_per_wind = covered_site_rate * GsTOKGh / average_wind
        prob_detect = 1 / (1 + np.exp(mdl[0] - mdl[1] * rate_per_wind))
        # Check the actual site rate against cutoff value
        if covered_site_rate <= (mdl[2] * GsTOKGh):
            site[missed_leaks_str] += n_leaks
            self.timeseries[missed_leaks_str][self.state["t"].current_timestep] += n_leaks
        elif np.random.binomial(1, prob_detect):
            found_leak = True
            site_measured_rate = measured_rate(covered_site_rate, self.config["sensor"]["QE"])
        else:
            site[missed_leaks_str] += n_leaks
            self.timeseries[missed_leaks_str][self.state["t"].current_timestep] += n_leaks
    elif self.config["measurement_scale"] == "equipment":
        for rate in covered_equipment_rates:
            m_rate = measured_rate(rate, self.config["sensor"]["QE"])
            rate_per_wind = rate * GsTOKGh / average_wind
            prob_detect = 1 / (1 + np.exp(mdl[0] - mdl[1] * rate_per_wind))
            if rate <= (mdl[2] * GsTOKGh):
                m_rate = 0
            elif np.random.binomial(1, prob_detect):
                found_leak = True
            else:
                m_rate = 0
            equip_measured_rates.append(m_rate)
            site_measured_rate += m_rate

            if not found_leak:
                site[missed_leaks_str] += 1
                self.timeseries[missed_leaks_str][self.state["t"].current_timestep] += n_leaks
    elif self.config["measurement_scale"] == "component":
        for leak in covered_leaks:
            rate_per_wind = leak["rate"] * GsTOKGh / average_wind
            prob_detect = 1 / (1 + np.exp(mdl[0] - mdl[1] * rate_per_wind))
            if prob_detect >= 1:
                prob_detect = 1
            if leak["rate"] <= (mdl[2] * GsTOKGh):
                site[missed_leaks_str] += 1
                self.timeseries[missed_leaks_str][self.state["t"].current_timestep] += 1
            elif np.random.binomial(1, prob_detect):
                found_leak = True
                meas_rate = measured_rate(leak["rate"], self.config["sensor"]["QE"])
                is_new_leak = update_tag(
                    leak,
                    meas_rate,
                    site,
                    self.timeseries,
                    self.state["t"],
                    self.config["label"],
                    self.id,
                    self.program_parameters,
                )
                if is_new_leak:
                    site_measured_rate += meas_rate
            else:
                site[missed_leaks_str] += 1
                self.timeseries[missed_leaks_str][self.state["t"].current_timestep] += 1
    site_dict = {
        "site": site,
        "leaks_present": covered_leaks,
        "site_true_rate": site_rate,
        "site_measured_rate": site_measured_rate,
        "equip_measured_rates": equip_measured_rates,
        "vent_rate": venting,
        "found_leak": found_leak,
    }
    return site_dict