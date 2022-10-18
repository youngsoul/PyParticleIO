from pyparticleio.ParticleCloud import ParticleCloud
from dotenv import load_dotenv
import os

if __name__ == '__main__':
    load_dotenv("./.env")
    c = ParticleCloud(username_or_access_token=os.getenv("ACCESS_TOKEN"))
    devices = c.devices_list
    print(devices)

    for device in devices:
        print(device.name)
        print(device.attribute_names())

    device_name = "bacon_captain"
    print("-"*10)
    print(c.devices[device_name])

