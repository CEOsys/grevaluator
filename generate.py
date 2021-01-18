#!/usr/bin/env python

from pathlib import Path
import yaml
from passlib.context import CryptContext
from secrets import token_hex

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

path = Path(__file__).parent.absolute()
secret_key = token_hex(32)
password = token_hex(32)
username = "testuser"


username_magicapp = input("MAGICapp login email: ")
password_magicapp = input("MAGICapp password: ")

print("Writing .env file in guideline server")
with open(path / "apps/guideline-server/.env", "w") as f:
    f.write(f'MAGICAPP_EMAIL="{username_magicapp}"\n')
    f.write(f'MAGICAPP_PASSWORD="{password_magicapp}"\n')

print("Writing .env file in viz app")
with open(path / "apps/viz/.env", "w") as f:
    f.write(f'VIZ_BACKEND_USERNAME="{username}"\n')
    f.write(f'VIZ_BACKEND_PASSWORD="{password}"\n')

print("Writing .env file in viz backend")
with open(path / "apps/viz-backend/.env", "w") as f:
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
print("Writing users_db.yml in viz backend")
with open(path / "apps/viz-backend/auth/users_db.yml", "w") as outfile:
    yaml.dump(users_db, outfile)
