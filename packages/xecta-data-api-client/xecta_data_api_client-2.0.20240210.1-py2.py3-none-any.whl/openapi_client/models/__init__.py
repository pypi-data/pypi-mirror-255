# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from openapi_client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from openapi_client.model.allocation import Allocation
from openapi_client.model.allocation_input import AllocationInput
from openapi_client.model.casing import Casing
from openapi_client.model.casing_input import CasingInput
from openapi_client.model.daily_production import DailyProduction
from openapi_client.model.daily_production_input import DailyProductionInput
from openapi_client.model.deviation_survey import DeviationSurvey
from openapi_client.model.deviation_survey_input import DeviationSurveyInput
from openapi_client.model.down_hole_equipment import DownHoleEquipment
from openapi_client.model.down_hole_equipment_input import DownHoleEquipmentInput
from openapi_client.model.esp_input import ESPInput
from openapi_client.model.esp import Esp
from openapi_client.model.formation import Formation
from openapi_client.model.formation_input import FormationInput
from openapi_client.model.gas_lift_valve import GasLiftValve
from openapi_client.model.gas_lift_valve_input import GasLiftValveInput
from openapi_client.model.micro_string import MicroString
from openapi_client.model.micro_string_input import MicroStringInput
from openapi_client.model.sucker_rod_pump import SuckerRodPump
from openapi_client.model.sucker_rod_pump_input import SuckerRodPumpInput
from openapi_client.model.time_series import TimeSeries
from openapi_client.model.time_series_history import TimeSeriesHistory
from openapi_client.model.time_series_history_input import TimeSeriesHistoryInput
from openapi_client.model.time_series_input import TimeSeriesInput
from openapi_client.model.tubing import Tubing
from openapi_client.model.tubing_input import TubingInput
from openapi_client.model.well import Well
from openapi_client.model.well_input import WellInput
from openapi_client.model.wellbore import Wellbore
from openapi_client.model.wellbore_input import WellboreInput
