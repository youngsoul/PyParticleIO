from pyparticleio.ParticleCloud import ParticleCloud
from dotenv import load_dotenv
import os

if __name__ == '__main__':
    load_dotenv("./.env")
    c = ParticleCloud(username_or_access_token=os.getenv("ACCESS_TOKEN"))

    device_name = "bacon_captain"
    device = c.devices[device_name]

    print(device.attribute_names())
    for attr_name in device.attribute_names():
        print(attr_name, "->", device.attribute(attr_name))
