from pyparticleio.ParticleCloud import ParticleCloud
from dotenv import load_dotenv
import os
device_name = "bacon_captain"

if __name__ == '__main__':
    load_dotenv("./.env")
    c = ParticleCloud(username_or_access_token=os.getenv("ACCESS_TOKEN"))

    print("-"*10)
    print(c.devices[device_name].variables)
    print(c.bacon_captain.variables)

    print(c.bacon_captain.temp)
    print(c.devices[device_name].variable("temp"))
    print(c.bacon_captain.variable("temp"))

    print(c.bacon_captain.humidity)
    print(c.devices[device_name].variable("humidity"))

    print("wifi strength", "->", c.bacon_captain.wifi, "of 10")
