# ------------------------------------------------------------------------------
# Program:     The LDAR Simulator (LDAR-Sim)
# File:        initialization.versioning
# Purpose:     Checks for the versions of the parameter files
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


def check_major_version(version_string, major_version):
    try:
        major_part, minor_part = map(str, version_string.split("."))
        return major_part == major_version
    except ValueError:
        return False


LEGACY_PARAMETER_WARNING = (
    "\nLDAR-Sim has detected an attempt to run a simulation model"
    " with legacy parameter files. \n\n"
    "If the goal is to reproduce previously modelled results"
    " using the legacy parameters, please download the version"
    " of LDAR-Sim used to produce those results.\n"
    "Versioned releases can be found at: https://github.com/LDAR-Sim/LDAR_Sim/releases.\n\n"
    "Otherwise, please visit: "
    "https://github.com/LDAR-Sim/LDAR_Sim/blob/master/ParameterMigrationGuide.md"
    " for guidance on how to update parameter files to the latest version.\n"
    "Please rerun the model once you have successfully"
    " migrated your parameters to the latest version. \n\n"
    "See https://github.com/LDAR-Sim/LDAR_Sim/blob/master/changelog.md"
    " to find a record of what has changed with LDAR-Sim\n"
)

MINOR_VERSION_MISMATCH_WARNING = (
    "\nLDAR-Sim has detected an attempt to run a simulation model"
    " with out of date parameter files. \n\n"
    "New Parameters may have been introduced since the creation "
    "of the parameter files currently in use.\n"
    "See https://github.com/LDAR-Sim/LDAR_Sim/blob/master/changelog.md"
    " to find a record of what has changed with LDAR-Sim\n"
)

MAJOR_VERSION_ONLY_WARNING = (
    "\nLDAR-Sim has detected an attempt to run a simulation model"
    " with a single number version. \n\n"
    "Standard parameter version numbers include a major and a minor "
    " version number, for example: 3.0. \n\n"
    "Please update the version to a valid version and rerun LDAR-Sim. \n\n"
)

CURRENT_MAJOR_VERSION = "3"

CURRENT_MINOR_VERSION = "3"

CURRENT_FULL_VERSION = "3.3"
