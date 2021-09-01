#!/usr/bin/env python
from typing import Union, Optional, List, Any
import datetime
import pandas as pd
import numpy as np
from pathlib import Path
import yaml
from passlib.context import CryptContext
from secrets import token_hex

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

path = Path(__file__).parent.absolute()
secret_key = token_hex(32)
password = token_hex(32)
username = "testuser"


def yes_or_no(question: str) -> bool:
    """
    Requests a (y)es or (n)o answer to a question from the user

    Args:
        question: The question to ask

    Returns: True if user answered yes, False if user answered no

    """
    while "the answer is invalid":
        reply = str(input(question + " (y/n): ")).lower().strip()
        if reply[0] == "y":
            return True
        if reply[0] == "n":
            return False


use_magicapp = yes_or_no(
    "Use magicapp to read guidelines (you need a valid magicapp login for this)"
)

username_magicapp: Optional[str]
password_magicapp: Optional[str]

if use_magicapp:
    username_magicapp = input("MAGICapp login email: ")
    password_magicapp = input("MAGICapp password: ")
else:
    username_magicapp = None
    password_magicapp = None

print("Writing .env file in guideline interface")
with open(path / "apps/guideline-interface/app/.env", "w") as f:
    f.write(f"MAGICAPP_USE={int(use_magicapp)}\n")
    f.write(f'MAGICAPP_EMAIL="{username_magicapp}"\n')
    f.write(f'MAGICAPP_PASSWORD="{password_magicapp}"\n')

print("Writing .env file in ui app")
with open(path / "apps/ui/app/.env", "w") as f:
    f.write(f'UI_BACKEND_USERNAME="{username}"\n')
    f.write(f'UI_BACKEND_PASSWORD="{password}"\n')

print("Writing .env file in ui backend")
with open(path / "apps/ui-backend/app/.env", "w") as f:
    f.write(f'SECRET_KEY="{secret_key}"\n')

users_db = {
    "testuser": {
        "username": username,
        "full_name": "Test User",
        "email": "testuser@example.com",
        "hashed_password": pwd_context.hash(password),
        "disabled": False,
    }
}
print("Writing users_db.yml in ui backend")
with open(path / "apps/ui-backend/app/auth/users_db.yml", "w") as outfile:
    yaml.dump(users_db, outfile)


def random_dates(
    start: Union[str, datetime.datetime],
    end: Union[str, datetime.datetime],
    count: int = 1,
) -> pd.Series:
    """
    Generates a list of random dates in a given range

    Args:
        start: Minimum date (str or datetime)
        end: Maximal date (str or datetime)
        count: Number of dates to create

    Returns: Series of random dates between start and end

    """
    start_u = pd.to_datetime(start).value // 10 ** 9
    end_u = pd.to_datetime(end).value // 10 ** 9

    s = pd.to_datetime(np.random.randint(start_u, end_u, count), unit="s")

    return s.sort_values()


class Variable:
    """
    Variable value generator base class

    Args:
        name: Name of the variable
        min: Minimal value of the variable (for numeric and datetime variables)
        max: Maximal value of the variable (for numeric and datetime variables)
        count: Number of variable values to generate (only count or rate may be set, not both)
        rate: Rate of variable values to generate in 1/day (e.g. if rate = 4, 4 values will be generated for each day in the supplied range)
        options: Valid options for Multiple choice variables (ChoiceVariable class)
        rate_fixed: If true and rate is set, then the timepoint of each value will be on an equidistant grid. If false, the timepoints will be drawn randomly.
        time_window: If true, then an end datetime for each variable is also generated, i.e. each value will define a time window rather than a single time point
        min_values: Minimal number of values to create for this variable
        value: Value to use for FixedVariable
    """

    def __init__(
        self,
        name: str,
        *,
        min: Optional[Union[float, int]] = None,
        max: Optional[Union[float, int]] = None,
        count: Optional[int] = None,
        rate: Optional[float] = None,
        options: Optional[List] = None,
        rate_fixed: bool = True,
        time_window: bool = False,
        min_values: int = 1,
        value: Optional[Any] = None,
    ):
        self.name = name
        self.min = min
        self.max = max
        self.count = count
        self.rate = rate
        self.options = options
        self.rate_fixed = rate_fixed
        self.time_window = time_window
        self.min_values = min_values
        self.value = value

        if rate is not None and count is not None:
            raise ValueError("cannot supply rate and count at the same time")

    def sample(self, start: datetime.datetime, end: datetime.datetime) -> pd.DataFrame:
        """
        Sample data for this variable in the specified datetime range

        Args:
            start: Start of the datetime range for which data will be generated
            end: End of the datetime range for which data will be generated

        Returns: Pandas dataframe with generated sample values and time points / ranges

        """

        if self.count is not None:
            count = self.count
        elif self.rate is not None:
            length_d = (end - start).total_seconds() / 86400
            count = int(length_d * self.rate)

        count = max(count, self.min_values)

        values = self._sample_values(count)
        dates = self._sample_dates(start, end, count)
        dates = dates.astype("datetime64[s]")

        if self.time_window:
            dates_end = dates.shift(-1)
        else:
            dates_end = [None] * count

        df = pd.DataFrame(
            {
                "variable_name": [self.name] * count,
                "value": values,
                "datetime": dates,
                "datetime_end": dates_end,
            }
        )

        return df

    def _sample_values(self, count: int) -> List:
        """
        Sample the desired number of values for the variable

        Abstract function, must be overwritten in actual variable classes

        Args:
            count: Number of values to generate

        Returns: List of generated values

        """
        raise NotImplementedError()

    def _sample_dates(
        self, start: datetime.datetime, end: datetime.datetime, count: int
    ) -> pd.Series:
        """
        Sample the desired number of time points for the variable

        Args:
            start: Start of the datetime range
            end: End of the datetime range
            count: Number of time points to generate in the given datetime range

        Returns: Pandas Series with time points

        """
        if self.rate_fixed:
            dates = pd.date_range(start=start, end=end, periods=count)
        else:
            dates = random_dates(start=start, end=end, count=count)

        return dates.to_series().reset_index(drop=True)


class IntVariable(Variable):
    """
    Integer variable generator - generates data points with random integer values in the given range
    from an underlying uniform distribution.

    Required parameters: name, min, max, count or rate
    Optional parameters: rate_fixed, time_window, min_values
    """

    def _sample_values(self, count: int) -> List:
        return np.random.randint(self.min, self.max, count)


class ChoiceVariable(Variable):
    """
    Multiple choice variable generator - generates data points with values randomly chosen from an explicit list

    Required parameters: name, options, count or rate
    Optional parameters: rate_fixed, time_window, min_values
    """

    def _sample_values(self, count: int) -> List:
        return np.random.choice(self.options, count)


class FloatVariable(Variable):
    """
    Float variable generator (uniform random) - generates data points with random float values in the given range
    from an underlying uniform distribution.

    Required parameters: name, min, max, count or rate
    Optional parameters: rate_fixed, time_window, min_values
    """

    def _sample_values(self, count: int) -> List:
        return np.random.random_sample(count) * (self.max - self.min) + self.min


class GaussianVariable(Variable):
    """
    Float variable generator (gaussian random distribution) - generates data points with random float values in the
    given range from an underlying Gaussian distribution.
    The mean and standard deviation of the underlying gaussian distribution are derived from min and max parameters.

    Required parameters: name, min, max, count or rate
    Optional parameters: rate_fixed, time_window, min_values
    """

    def _sample_values(self, count: int) -> List:
        mean = (
            self.max - self.min
        ) / 2  # use 1/2 of the range as the mean of the Gaussian distribution
        sigma = (
            self.max - self.min
        ) / 5  # use 1/5 of the range as the standard deviation of the Gaussian distribution

        values = np.random.randn(count) * sigma + mean
        return np.clip(values, self.min, self.max)


class BoolVariable(Variable):
    """
    Boolean variable generator

    Required parameters: name, count or rate
    Optional parameters: rate_fixed, time_window, min_values
    """

    def _sample_values(self, count: int) -> List:
        return np.random.randint(0, 2, count) == 1


class EventVariable(Variable):
    """
    Event variable generator - generates data points at random time points according to the given rate.

    This will generate values at the given rate with a probability of 50% (i.e. approximately half of the generated
    values are dropped)

    Required parameters: name, value, count or rate
    Optional parameters: rate_fixed, time_window, min_values
    """

    def _sample_values(self, count: int) -> List:
        return [self.value] * count

    def sample(self, start: int, end: int) -> pd.DataFrame:
        """
        Sample data for this variable in the specified datetime range

        Args:
            start: Start of the datetime range for which data will be generated
            end: End of the datetime range for which data will be generated

        Returns: Pandas dataframe with generated sample values and time points / ranges

        """
        df = super().sample(start, end)

        valid_events = np.random.randint(0, 2, len(df)) == 1
        df = df.iloc[valid_events].copy()

        return df


class DateTimeVariable(Variable):
    """
    Datetime variable generator - generates data points with random datetime values in a given range.

    Required parameters: name, min, max, count or rate
    Optional parameters: rate_fixed, time_window, min_values
    """

    def _sample_values(self, count: int) -> List:
        return random_dates(start=self.min, end=self.max, count=count)


class FixedVariable(Variable):
    """
    Fixed value variable generator - generates data points with a fixed value.


    Required parameters: name, value, count or rate
    Optional parameters: rate_fixed, time_window, min_values
    """

    def _sample_values(self, count: int) -> List:
        return [self.value] * count


np.random.seed(1234)  # fix seed for reproducibility
now = datetime.datetime.now()

# admission time point
adm = random_dates(now - pd.Timedelta("100d"), now - pd.Timedelta("1d"))[0]

# list of variables to generate
variables = [
    IntVariable("RASS", min=-5, max=4, rate=1),
    IntVariable("SOFA", min=0, max=18, rate=3),
    ChoiceVariable(
        "body_position",
        options=["supine", "lateral", "upright", "prone", "self"],
        rate=2,
        rate_fixed=False,
        time_window=True,
    ),
    IntVariable("deltaSOFA", min=-15, max=13, rate=3),
    GaussianVariable("oxygenation_index_calc", min=31.2, max=600, rate=96),
    GaussianVariable("respiratory_minute_volume", min=0, max=30, rate=96),
    GaussianVariable("respiratory_rate", min=0, max=40, rate=96),
    FloatVariable("sO2", min=80, max=100, rate=96),
    IntVariable("ventilation_mode", min=0, max=4, rate=3, time_window=True),
    ChoiceVariable("ward", options=["101i", "102i", "103i"], count=1),
    BoolVariable("test_covid19_pcr", rate=0.1),
    EventVariable("drug_dexamethason_bolus", rate=1, value=1),
    DateTimeVariable(
        "birth_date",
        count=1,
        min=datetime.datetime.now() - (pd.Timedelta("365d") * 80),
        max=datetime.datetime.now() - (pd.Timedelta("365d") * 18),
    ),
    FixedVariable("admission_hospitalisation", count=1, value=adm),
]

print("Generating patient sample data")

n_pat = 50
tz = "Europe/Berlin"
res = []

for i_pat in range(n_pat):
    patient_id = f"P{i_pat:06d}"

    df = pd.concat([var.sample(adm, now) for var in variables])
    df["pseudo_fallnr"] = patient_id
    res.append(df)
df = pd.concat(res).reset_index(drop=True)

df["datetime"] = df["datetime"].dt.tz_localize("UTC").dt.tz_convert(tz)
df["datetime_end"] = (
    df["datetime_end"].apply(pd.to_datetime).dt.tz_localize("UTC").dt.tz_convert(tz)
)
idx_dt = pd.to_datetime(df["value"], errors="coerce").notnull()

df.loc[idx_dt, "value"] = (
    pd.to_datetime(df.loc[idx_dt, "value"]).dt.tz_localize("UTC").dt.tz_convert(tz)
)

df.to_pickle(
    path
    / "apps"
    / "clinical-data-interface"
    / "data"
    / "sample_data_shuffle_large.pkl.gz",
    protocol=3,
)

print("done")
