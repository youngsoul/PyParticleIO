from pyparticleio.ParticleCloud import ParticleCloud
from dotenv import load_dotenv
import os


def _event_call_back(event_data):
    print("Event CallBack: " + str(event_data))


if __name__ == '__main__':
    load_dotenv("./.env")
    c = ParticleCloud(username_or_access_token=os.getenv("ACCESS_TOKEN"))
    devices = c.devices_list
    print(devices)

    print("Subscribing to 'temp' event, then waiting to watch events come in")
    c.bacon_captain.subscribe('temp', _event_call_back)
    c.bacon_captain.subscribe('wifi', _event_call_back)
    c.bacon_captain.subscribe('humidity', _event_call_back)
    c.bacon_captain.subscribe('notthere', _event_call_back)

    value = input("Enter any key to stop waiting:\n")

    print("Unsubscribing....")
    c.bacon_captain.unsubscribe('temp')
    c.bacon_captain.unsubscribe('wifi')
    c.bacon_captain.unsubscribe('humidity')
    c.bacon_captain.unsubscribe('notthere')

    print("Wait for the notification that the listener is unsubscribed....")
    value = input("Enter any key to stop waiting:\n")

    print("Done")



