import requests
import threading
from sseclient import SSEClient
from hammock import Hammock
import traceback

requests.packages.urllib3.disable_warnings()

"""
    Inspired heavily from:
    https://github.com/Alidron/spyrk/blob/master/spyrk/spark_cloud.py
    -- Thank you for sharing your implementation

    The only reason I did not just use yours, was to go through the
    process so I could learn more of the Python constructs that you used.

    ** Create Instance of ParticleCloud
    particle_cloud = ParticleCloud(access_token)
    particle_cloud = ParticleCloud(username, password)
    particle_cloud = ParticleCloud(access_token, device_ids=[only consider these ids])

    ** List Devices
    particle_cloud.devices

    ** Call a function
    particle_cloud.internet_button1.ledOn('led1')

    ** Get a variable value
    particle_cloud.internet_button1.buttonCount

    ** Subscribe for a device specific event.
    def callback(event_data):
         print("event callback")

    particle_cloud.internet_button1.subscribe("button1", callback)

    ** Subscribe for a non-device specific event
    particle_cloud.internet_button1.cloud_subscribe("button2", callback)

    ** Publish an event to the cloud
    particle_cloud.internet_button1.publish("do_rainbow")



https://docs.particle.io/reference/api/
"""


class ParticleDeviceException(Exception):
    def __init__(self, message, errors=None):
        super(ParticleDeviceException, self).__init__(message)
        self.errors = errors


class ParticleCloud(object):
    """
    Provides access to the Particle cloud to call function, read variables,
    subscribe for events and publish events.
    """
    API_PREFIX = 'https://api.particle.io/v1'

    def __init__(self, username_or_access_token, password=None, device_ids=None):
        """

        :param username_or_access_token: if access token, then no password is required
        :param password:
        :param device_ids: list of device ids to consider.  only these devices will be part of the dynamic API
                            if None, then all device ids are pulled from Particle Cloud
        """
        self.particle_cloud_api = Hammock(ParticleCloud.API_PREFIX + "/devices")
        if password is None:
            self.access_token = username_or_access_token
        else:
            self.access_token = self._login(username_or_access_token, password)

        self.device_ids = device_ids
        self._get_devices()

    @staticmethod
    def wait_forever(self):
        while True:
            try:
                time.sleep(3600)
            except:
                continue

    @staticmethod
    def _check_error(response):
        """Raises an exception if the Particle Cloud returned an error."""
        if (not response.ok) or (response.status_code != 200):
            raise Exception(
                response.json()['error'] + ': ' +
                response.json()['error_description']
            )

    def _login(self, username, password):
        data = {
            'username': username,
            'password': password,
            'grant_type': 'password'
        }

        # https://docs.particle.io/reference/api/
        # You must give a valid client ID and password in HTTP Basic Auth.
        # For controlling your own developer account, you can use particle:particle.
        res = self.particle_cloud_api.oauth.token.POST(auth=('particle', 'particle'), data=data)
        self._check_error(res)
        return res.json()['access_token']

    def _get_devices(self):
        """Create a dictionary of devices known to the user account."""
        params = {'access_token': self.access_token}
        res = self.particle_cloud_api.GET(params=params)
        self._check_error(res)
        json_list = res.json()

        self.devices = {}
        if json_list:
            for d in json_list:
                if self.device_ids is None or (self.device_ids is not None and d['id'] in self.device_ids):
                    info = self._get_device_info(d['id'])
                    d['functions'] = info['functions']
                    d['variables'] = info['variables']
                    d['device_id'] = d['id']  # my preference is to call it device_id
                    d['particle_device_api'] = self.particle_cloud_api(d['id'])
                    d['access_token'] = self.access_token

                    self.devices[d['name']] = _ParticleDevice(**d)

    def _get_device_info(self, device_id):
        """
            Queries the Particle Cloud for detailed information about a device.
        """
        params = {'access_token': self.access_token}
        r = self.particle_cloud_api(device_id).GET(params=params)
        self._check_error(r)
        return r.json()

    def __getattr__(self, name):
        """
            Returns a Device object as an attribute of the ParticleCloud object.

            accessed like:
            particle_cloud_variable.device_name

        """
        if name in self.devices:
            return self.devices[name]
        else:
            raise AttributeError()


class _ParticleDevice(object):
    """
    This class is not meant to be used directly.  Access a device by going
    through the ParticleCloud instance.  e.g.

    particleCloud.device_name.<function>|variable|subscribe|publish
    """
    @staticmethod
    def _check_error(response):
        """Raises an exception if the Particle Cloud returned an error."""
        if (not response.ok) or (response.status_code != 200):
            json_response = response.json()
            execption_msg = "HTTP Status Code: {0}.  ".format(response.status_code)
            if 'error' in json_response:
                execption_msg += "  Error: {0}".format(json_response['error'])

            if 'error_description' in json_response:
                execption_msg += "  Error: {0}".format(json_response['error_description'])

            raise Exception(execption_msg)

    def __init__(self, particle_device_api=None, device_id=None, access_token=None, functions=None, variables=None,
                 connected=None, **kwargs):
        self.device_id = device_id
        self.access_token = access_token
        self.particle_device_api = particle_device_api
        self.functions = functions
        self.variables = variables
        self.connected = connected

    def __getattr__(self, name):
        """
        Returns virtual attributes corresponding to function or variable
        names.
        """
        headers = {'Authorization': 'Bearer ' + self.access_token}

        if name == 'subscribe':
            def subscribe_call(*args):
                # args[0] - event name
                # args[1] - event callback function
                self._add_device_event_listener(args[0], args[1])

            return subscribe_call

        elif name == 'cloud_subscribe':
            def device_subscribe_call(*args):
                # args[0] - event name
                # args[1] - event callback function
                self._add_event_listener(args[0], args[1])

            return device_subscribe_call

        elif name == 'publish':
            def publish_call(*args):
                # args[0] - event name
                # args[1] - event data
                # args[2] - private
                # args[3] - ttl
                event_name = None
                event_data = None
                event_private = True
                event_ttl = 60

                if len(args) >= 1:
                    event_name = args[0]

                if len(args) >= 2:
                    event_data = args[1]

                if len(args) >= 3:
                    event_private = args[2]

                if len(args) == 4:
                    event_ttl = args[3]

                self._publish_event(event_name, event_data, event_private, event_ttl)

            return publish_call

        elif name in self.functions:
            def fcall(*args):
                data = {'args': ','.join(args)}
                res = self.particle_device_api(name).POST(headers=headers, params={}, data=data)
                self._check_error(res)
                return res.json()['return_value']

            return fcall

        elif name in self.variables:
            res = self.particle_device_api(name).GET(headers=headers, params={})
            self._check_error(res)
            return res.json()['result']

        else:
            raise AttributeError(name + " was not found")

    def _event_loop(self, event_name, call_back, url):
        while True:
            try:
                print("Create SSEClient for url: {0}".format(url))
                sse_client = SSEClient(url=url, retry=5000)
                # we never leave the for loop because this loop
                # calls the _next_ method of the sseclient
                # so it sits here and just waits for messages to be receieved.
                # the for loop below can be thought of as equivalent to
                # while True:
                #   msg = sse_client.next(5000)
                #   if msg is not None:
                #      _process_msg(msg)
                #
                for msg in sse_client:
                    if len(str(msg)) > 0:
                        call_back(msg)
            except Exception as exc:
                print("Error in event loop [{0}],[{1}],[{2}]".format(event_name, url, traceback.print_exc()))
                time.sleep(60)
                print("Reconnect to SSEClient")
                continue

        print("you will never get here because the for loop calls an iterator")

    def _add_event_listener(self, event_name, call_back):
        """
        Adds a non-device specific event listener.  Any device associated with
        the access token throwing an event will be caught by a listener

        This is a non-blocking call.

        :param event_name:
        :param call_back:
        :return: None
        """
        if event_name is None:
            raise ParticleDeviceException(message="Invalid Event Name.  An Event name must be provided.")

        url = ParticleCloud.API_PREFIX + "/devices/events/{0}?access_token={1}".format(event_name, self.access_token)
        t = threading.Thread(target=self._event_loop, args=(event_name, call_back, url))
        t.daemon = True
        t.start()

    def _add_device_event_listener(self, event_name, call_back):
        """
        Add a device specific event listener.  Only events thrown by this particular
        device will have events caught

        This is a non-blocking call
        :param event_name:
        :param call_back:
        :return: None
        """
        if event_name is None:
            raise ParticleDeviceException(message="Invalid Event Name.  An Event name must be provided.")

        url = ParticleCloud.API_PREFIX + "/devices/{0}/events/{1}?access_token={2}".format(self.device_id, event_name,
                                                                                           self.access_token)
        t = threading.Thread(target=self._event_loop, args=(event_name, call_back, url))
        t.daemon = True
        t.start()

    def _publish_event(self, event_name, event_data=None, private=True, ttl=60):
        if event_name is None:
            raise ParticleDeviceException(message="Event Name cannot be none")
        payload = {
            "name": event_name,
            "private": private,
            "ttl": ttl
        }
        if event_data is not None:
            payload['data'] = event_data

        url = ParticleCloud.API_PREFIX + "/devices/events"
        headers = {'Authorization': 'Bearer ' + self.access_token}
        res = requests.post(url, data=payload, params=None, headers=headers, verify=False)

        if res.status_code != 200:
            raise ParticleDeviceException(message="Invalid return status code: {0}".format(res.status_code))

        return res.text



if __name__ == "__main__":
    import time
    import sys

    if len(sys.argv) != 2:
        raise Exception("Usage: ParticleCloud.py <access token>")

    access_token = sys.argv[1]

    def _event_call_back(event_data):
        print("Event CallBack: " + str(event_data))


    def _event_call_back2(event_data):
        print("Event CallBack2: " + str(event_data))

    test_name = "event subscribe"

    c = ParticleCloud(username_or_access_token=access_token)
    print(c.devices)

    if test_name == "variable":
        var = c.internet_button1.buttonCount
        print(str(var))
    elif test_name == "function":
        for f in c.internet_button1.functions:
            print(f)

        rtn = c.internet_button1.doReset("led1")
        print(str(rtn))
    elif test_name == "event subscribe":
        c.internet_button1.cloud_subscribe('button3', _event_call_back)
        c.internet_button1.subscribe('button4', _event_call_back2)

        while True:
            print("\nPhoton Event Subscribe: {0} {1}".format(time.strftime("%x"), time.strftime("%X")))
            time.sleep(300)
    elif test_name == "event publish":
        rtn = c.internet_button1.publish("do_rainbow")
        print("Publish Event: " + str(rtn))

    elif test_name == "function_led":
        for i in range(1,12):
            cmd = "{0},blue".format(i)
            rtn = c.internet_button2.ledOn(cmd)
            print("function_led({0}): {1}".format(cmd, str(rtn)))
            time.sleep(1)

        for i in range(1,12):
            cmd = "{0}".format(i)
            rtn = c.internet_button2.ledOff(cmd)
            print("function_led({0}): {1}".format(cmd, str(rtn)))
            time.sleep(1)

        c.internet_button2.ledOn("0,green")
        time.sleep(3)
        c.internet_button2.ledOff("0")
        time.sleep(3)

