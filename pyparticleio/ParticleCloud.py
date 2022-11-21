import requests
import threading
from sseclient import SSEClient
from hammock import Hammock
import traceback
import json

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

    def __init__(self, username_or_access_token, password=None, device_ids=None, api_prefix='https://api.particle.io/v1', **kwargs):
        """

        :param username_or_access_token: if access token, then no password is required
        :param password:
        :param device_ids: list of device ids to consider.  only these devices will be part of the dynamic API
                            if None, then all device ids are pulled from Particle Cloud
        :param api_prefix: base url of API server, defaults to https://api.particle.io/v1
        :param **kwargs: hammock session will be initiated with passed kwargs. So if you like to use an http proxy
                            pass your proxies dictionary here

        """

        self.particle_cloud_api = Hammock(api_prefix + "/devices", **kwargs)
        self.api_prefix = api_prefix
        if password is None:
            self.access_token = username_or_access_token
        else:
            self.access_token = self._login(username_or_access_token, password)

        self.device_ids = device_ids
        self.devices = self._get_devices()
        self.devices_list = []
        for k,v in self.devices.items():
            self.devices_list.append(v)

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

        temp_devices = {}
        if json_list:
            for d in json_list:
                if self.device_ids is None or (self.device_ids is not None and d['id'] in self.device_ids):
                    info = self.get_device_info(d['id'])
                    d['functions'] = info['functions']
                    d['variables'] = info['variables']
                    d['device_id'] = d['id']  # my preference is to call it device_id
                    d['particle_device_api'] = self.particle_cloud_api(d['id'])
                    d['access_token'] = self.access_token
                    d['api_prefix'] = self.api_prefix

                    temp_devices[d['name']] = _ParticleDevice(**d)

        return temp_devices

    def get_device_info(self, device_id):
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
                 connected=None, api_prefix=None, **kwargs):
        self.device_id = device_id
        self.access_token = access_token
        self.particle_device_api = particle_device_api
        self.functions = functions
        self.variables = variables
        self.connected = connected
        self.api_prefix = api_prefix
        self.other_attributes = kwargs
        self.event_listeners = {} # key: event name, value: listening thread

    def attribute_names(self):
        return list(self.other_attributes.keys()) + ['functions', 'variables', 'connected', 'api_prefix', 'device_id']

    def variable(self, variable_name):
        headers = {'Authorization': 'Bearer ' + self.access_token}

        res = self.particle_device_api(variable_name).GET(headers=headers, params={})
        self._check_error(res)
        return res.json()['result']

    def __getattr__(self, name):
        return self.attribute(name)

    def attribute(self, name):
        """
        Returns virtual attributes corresponding to function or variable
        names.
        """
        headers = {'Authorization': 'Bearer ' + self.access_token}

        if name == "functions":
            return self.functions
        elif name == "variables":
            return self.variables
        elif name == "connected":
            return self.connected
        elif name == "api_prefix":
            return self.api_prefix
        elif name == "device_id":
            return self.device_id
        elif name == 'subscribe':
            def subscribe_call(*args):
                # args[0] - event name
                # args[1] - event callback function
                self._add_device_event_listener(args[0], args[1])

            return subscribe_call

        elif name == 'unsubscribe':
            def unsubscribe_call(*args):
                # args[0] - event name
                self._remove_device_event_listener(args[0])
            return unsubscribe_call

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
            return self.variable(name)

        elif name in self.other_attributes:
            return self.other_attributes[name]

        else:
            raise AttributeError(name + " was not found")

    def _event_loop(self, event_name, call_back, url):
        exit_event_loop = False
        while True:
            if exit_event_loop:
                break
            try:
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
                        event_data = json.loads(str(msg))
                        event_data['event_name'] = event_name
                        call_back(event_data)
                        # check to see if the event_name is in the collection of event listenters
                        if event_name not in self.event_listeners.keys():
                            exit_event_loop = True
                            break # break out of the for msg loop, setting the exit event loop flag
            except Exception as exc:
                print("Error in event loop [{0}],[{1}]".format(event_name, traceback.print_exc()))
                time.sleep(60)
                print("Reconnect to SSEClient")
                continue

        # exiting the event loop

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

        url = self.api_prefix + "/devices/events/{0}?access_token={1}".format(event_name, self.access_token)
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

        if event_name in self.event_listeners.keys():
            return # this is already being subscribed to.

        url = self.api_prefix + "/devices/{0}/events/{1}?access_token={2}".format(self.device_id, event_name,
                                                                                           self.access_token)
        t = threading.Thread(target=self._event_loop, args=(event_name, call_back, url))
        t.daemon = True
        t.start()
        self.event_listeners[event_name] = t

    def _remove_device_event_listener(self, event_name):
        if event_name is None:
            raise ParticleDeviceException(message="Invalid Event Name.  An Event name must be provided.")
        if event_name in self.event_listeners.keys():
            self.event_listeners.pop(event_name, None)

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

        url = self.api_prefix + "/devices/events"
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

    '''
    # example how to initialize ParticleCloud with proxy support
    proxy_dict = {
        "proxies": {
            "https": "https://192.168.1.1:8080"
        }
    }
    c = ParticleCloud(username_or_access_token=access_token, **proxy_dict)
    '''

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

