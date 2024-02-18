"""Implementation of reward functions."""


from datetime import datetime
from math import exp
from typing import Any, Dict, List, Tuple, Union

from sinergym.utils.constants import LOG_REWARD_LEVEL, YEAR
from sinergym.utils.logger import Logger


class BaseReward(object):

    logger = Logger().getLogger(name='REWARD',
                                level=LOG_REWARD_LEVEL)

    def __init__(self):
        """
        Base reward class.

        All reward functions should inherit from this class.

        Args:
            env (Env): Gym environment.
        """

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Method for calculating the reward function."""
        raise NotImplementedError(
            "Reward class must have a `__call__` method.")


class LinearReward(BaseReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0
    ):
        """
        Linear reward function.

        It considers the energy consumption and the absolute difference to temperature comfort.

        .. math::
            R = - W * lambda_E * power - (1 - W) * lambda_T * (max(T - T_{low}, 0) + max(T_{up} - T, 0))

        Args:
            temperature_variables (List[str]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer session tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            energy_weight (float, optional): Weight given to the energy term. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
        """

        super(LinearReward, self).__init__()

        # Name of the variables
        self.temp_names = temperature_variables
        self.energy_names = energy_variables

        # Reward parameters
        self.range_comfort_winter = range_comfort_winter
        self.range_comfort_summer = range_comfort_summer
        self.W_energy = energy_weight
        self.lambda_energy = lambda_energy
        self.lambda_temp = lambda_temperature

        # Summer period
        self.summer_start = summer_start  # (month,day)
        self.summer_final = summer_final  # (month,day)

        self.logger.info('Reward function initialized.')

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Calculate the reward function.

        Args:
            obs_dict (Dict[str, Any]): Dict with observation variable name (key) and observation variable value (value)

        Returns:
            Tuple[float, Dict[str, Any]]: Reward value and dictionary with their individual components.
        """
        # Check variables to calculate reward are available
        try:
            assert all(temp_name in list(obs_dict.keys())
                       for temp_name in self.temp_names)
        except AssertionError as err:
            self.logger.error(
                'Some of the temperature variables specified are not present in observation.')
            raise err
        try:
            assert all(energy_name in list(obs_dict.keys())
                       for energy_name in self.energy_names)
        except AssertionError as err:
            self.logger.error(
                'Some of the energy variables specified are not present in observation.')
            raise err

        # Energy term
        energy, energy_values = self._get_energy(obs_dict)

        # Comfort
        comfort, temp_values = self._get_comfort(obs_dict)

        # Weighted sum of both terms
        energy_term, comfort_term, reward = self._get_reward(energy, comfort)

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'reward_weight': self.W_energy,
            'abs_energy': energy,
            'abs_comfort': comfort,
            'energy_values': energy_values,
            'temp_values': temp_values
        }

        return reward, reward_terms

    def _get_energy(self, obs_dict: Dict[str,
                                         Any]) -> Tuple[float,
                                                        List[float]]:
        """Calculate the reward term of the reward.

        Args:
            obs_dict (Dict[str, Any]): Observation to calculate the reward term.

        Returns:
            Tuple[float, List[float]]: Energy consumed (sum of variables) and List with energy_variable values used.
        """

        energy_values = [
            v for k, v in obs_dict.items() if k in self.energy_names]

        # The total energy is the sum of energies
        energy_value = sum(energy_values)

        return energy_value, energy_values

    def _get_comfort(self,
                     obs_dict: Dict[str,
                                    Any]) -> Tuple[float,
                                                   List[float]]:
        """Calculate the comfort term of the reward.

        Returns:
            Tuple[float, List[float]]: comfort penalty and List with temperatures used.
        """

        month = obs_dict['month']
        day = obs_dict['day_of_month']
        year = YEAR
        current_dt = datetime(int(year), int(month), int(day))

        # Periods
        summer_start_date = datetime(
            int(year),
            self.summer_start[0],
            self.summer_start[1])
        summer_final_date = datetime(
            int(year),
            self.summer_final[0],
            self.summer_final[1])

        if current_dt >= summer_start_date and current_dt <= summer_final_date:
            temp_range = self.range_comfort_summer
        else:
            temp_range = self.range_comfort_winter

        temp_values = [v for k, v in obs_dict.items() if k in self.temp_names]
        comfort = 0.0
        for T in temp_values:
            if T < temp_range[0] or T > temp_range[1]:
                comfort += min(abs(temp_range[0] - T), abs(T - temp_range[1]))

        return comfort, temp_values

    def _get_reward(self, energy: float,
                    comfort: float) -> Tuple[float, float, float]:
        """It calculates reward value using energy consumption and grades of temperature out of comfort range.

        Args:
            energy (float): Energy consumed
            comfort (float): Grades out of ranges

        Returns:
            Tuple[float,float,float]: reward term for energy , reward term for comfort and total reward calculated.
        """
        reward_energy = -self.lambda_energy * self.W_energy * energy
        reward_comfort = -self.lambda_temp * (1 - self.W_energy) * comfort
        reward = reward_energy + reward_comfort
        return reward_energy, reward_comfort, reward


class ExpReward(LinearReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0
    ):
        """
        Reward considering exponential absolute difference to temperature comfort.

        .. math::
            R = - W * lambda_E * power - (1 - W) * lambda_T * exp( (max(T - T_{low}, 0) + max(T_{up} - T, 0)) )

        Args:
            temperature_variables (List[str]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer session tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            energy_weight (float, optional): Weight given to the energy term. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
        """

        super(ExpReward, self).__init__(
            temperature_variables,
            energy_variables,
            range_comfort_winter,
            range_comfort_summer,
            summer_start,
            summer_final,
            energy_weight,
            lambda_energy,
            lambda_temperature
        )

    def _get_comfort(self,
                     obs_dict: Dict[str,
                                    Any]) -> Tuple[float,
                                                   List[float]]:
        """Calculate the comfort term of the reward.

        Returns:
            Tuple[float, List[float]]: comfort penalty and List with temperatures used.
        """

        month = obs_dict['month']
        day = obs_dict['day_of_month']
        year = YEAR
        current_dt = datetime(int(year), int(month), int(day))

        # Periods
        summer_start_date = datetime(
            int(year),
            self.summer_start[0],
            self.summer_start[1])
        summer_final_date = datetime(
            int(year),
            self.summer_final[0],
            self.summer_final[1])

        if current_dt >= summer_start_date and current_dt <= summer_final_date:
            temp_range = self.range_comfort_summer
        else:
            temp_range = self.range_comfort_winter

        temps = [v for k, v in obs_dict.items() if k in self.temp_names]
        comfort = 0.0
        for T in temps:
            if T < temp_range[0] or T > temp_range[1]:
                comfort += exp(min(abs(temp_range[0] - T),
                                   abs(T - temp_range[1])))

        return comfort, temps


class HourlyLinearReward(LinearReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        default_energy_weight: float = 0.5,
        lambda_energy: float = 1.0,
        lambda_temperature: float = 1.0,
        range_comfort_hours: tuple = (9, 19),
    ):
        """
        Linear reward function with a time-dependent weight for consumption and energy terms.

        Args:
            temperature_variables (List[str]]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer session tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            default_energy_weight (float, optional): Default weight given to the energy term when thermal comfort is considered. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
            range_comfort_hours (tuple, optional): Hours where thermal comfort is considered. Defaults to (9, 19).
        """

        super(HourlyLinearReward, self).__init__(
            temperature_variables,
            energy_variables,
            range_comfort_winter,
            range_comfort_summer,
            summer_start,
            summer_final,
            default_energy_weight,
            lambda_energy,
            lambda_temperature
        )

        # Reward parameters
        self.range_comfort_hours = range_comfort_hours
        self.default_energy_weight = default_energy_weight

    def __call__(self, obs_dict: Dict[str, Any]
                 ) -> Tuple[float, Dict[str, Any]]:
        """Calculate the reward function.

        Args:
            obs_dict (Dict[str, Any]): Dict with observation variable name (key) and observation variable value (value)

        Returns:
            Tuple[float, Dict[str, Any]]: Reward value and dictionary with their individual components.
        """
        # Check variables to calculate reward are available
        try:
            assert all(temp_name in list(obs_dict.keys())
                       for temp_name in self.temp_names)
        except AssertionError as err:
            self.logger.error(
                'Some of the temperature variables specified are not present in observation.')
            raise err
        try:
            assert all(energy_name in list(obs_dict.keys())
                       for energy_name in self.energy_names)
        except AssertionError as err:
            self.logger.error(
                'Some of the energy variables specified are not present in observation.')
            raise err

        # Energy term
        energy, energy_values = self._get_energy(obs_dict)

        # Comfort
        comfort, temp_values = self._get_comfort(obs_dict)

        # Determine reward weight depending on the hour
        hour = obs_dict['hour']
        if hour >= self.range_comfort_hours[0] and hour <= self.range_comfort_hours[1]:
            self.W_energy = self.default_energy_weight
        else:
            self.W_energy = 1.0

        # Weighted sum of both terms
        energy_term, comfort_term, reward = self._get_reward(energy, comfort)

        reward_terms = {
            'energy_term': energy_term,
            'comfort_term': comfort_term,
            'reward_weight': self.W_energy,
            'abs_energy': energy,
            'abs_comfort': comfort,
            'energy_values': energy_values,
            'temp_values': temp_values
        }

        return reward, reward_terms


class NormalizedLinearReward(LinearReward):

    def __init__(
        self,
        temperature_variables: List[str],
        energy_variables: List[str],
        range_comfort_winter: Tuple[int, int],
        range_comfort_summer: Tuple[int, int],
        summer_start: Tuple[int, int] = (6, 1),
        summer_final: Tuple[int, int] = (9, 30),
        energy_weight: float = 0.5,
        max_energy: float = 8,
        max_comfort: float = 12,
    ):
        """
        Linear reward function with a time-dependent weight for consumption and energy terms.

        Args:
            temperature_variables (List[str]]): Name(s) of the temperature variable(s).
            energy_variables (List[str]): Name(s) of the energy/power variable(s).
            range_comfort_winter (Tuple[int,int]): Temperature comfort range for cold season. Depends on environment you are using.
            range_comfort_summer (Tuple[int,int]): Temperature comfort range for hot season. Depends on environment you are using.
            summer_start (Tuple[int,int]): Summer session tuple with month and day start. Defaults to (6,1).
            summer_final (Tuple[int,int]): Summer session tuple with month and day end. defaults to (9,30).
            default_energy_weight (float, optional): Default weight given to the energy term when thermal comfort is considered. Defaults to 0.5.
            lambda_energy (float, optional): Constant for removing dimensions from power(1/W). Defaults to 1e-4.
            lambda_temperature (float, optional): Constant for removing dimensions from temperature(1/C). Defaults to 1.0.
            range_comfort_hours (tuple, optional): Hours where thermal comfort is considered. Defaults to (9, 19).
        """

        super(NormalizedLinearReward, self).__init__(
            temperature_variables,
            energy_variables,
            range_comfort_winter,
            range_comfort_summer,
            summer_start,
            summer_final,
            energy_weight
        )

        # Reward parameters
        self.max_energy = max_energy
        self.max_comfort = max_comfort

    def _get_reward(self, energy: float,
                    comfort: float) -> Tuple[float, float, float]:
        """It calculates reward value using energy consumption and grades of temperature out of comfort range. Aplying normalization

        Args:
            energy (float): Energy consumed
            comfort (float): Grades out of ranges

        Returns:
            Tuple[float,float,float]: reward term for energy , reward term for comfort and total reward calculated.
        """
        # Update max energy and comfort
        self.max_energy = max(self.max_energy, energy)
        self.max_comfort = max(self.max_comfort, comfort)
        # Calculate normalization
        energy_norm = 0 if energy == 0 else energy / self.max_energy
        comfort_norm = 0 if comfort == 0 else comfort / self.max_comfort
        # Calculate norm values
        reward_energy = -self.W_energy * energy_norm
        reward_comfort = -(1 - self.W_energy) * comfort_norm
        reward = reward_energy + reward_comfort
        return reward_energy, reward_comfort, reward
