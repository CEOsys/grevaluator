#  This file is part of CEOsys Recommendation Checker.
#
#  Copyright (c) 2021 CEOsys project team <https://covid-evidenz.de>.
#
#  CEOsys Recommendation Checker is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  CEOsys Recommendation Checker is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with CEOsys Recommendation Checker.  If not, see <https://www.gnu.org/licenses/>.
"""
Configuration file for CEOsys user interface backend.
"""


from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    FastAPI Settings for ui backend
    """

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    ceosys_data_path: str
    guideline_server: str
    patientdata_server: str

    class Config:
        """
        Config sub class for FastAPI settings
        """

        env_file = ".env"


settings = Settings()
