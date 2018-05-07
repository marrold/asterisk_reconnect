import errno
import re
import threading
import time
from asterisk.ami import SimpleAction, AMIClient


class asterisk_reconnect:
    def __init__(self, logger, config):

        self.logger = logger
        self.config = config
        self.clients = self.config['clients']

        self.check_interval = config['intervals']['check_interval']
        self.reconnect_interval = config['intervals']['reconnect_interval']
        self.ping_interval = config['intervals']['ping_interval']

        self.ami_host = config['ami']['host']
        self.ami_port = int(config['ami']['port'])
        self.ami_username = config['ami']['username']
        self.ami_password = config['ami']['password']

        self.ami_client = AMIClient(address=self.ami_host, port=self.ami_port)
        self.channels = []
        self.last_check = time.time()
        self.last_ping = time.time()
        self.last_login = time.time()
        self.connected = False

        self.kill_received = False
        self.thread = threading.Thread(target=self.reconnect_loop, args=())
        self.thread.daemon = True
        self.thread.start()

    def login(self):

        self.last_login = time.time()

        self.ami_client = AMIClient(address=self.ami_host, port=self.ami_port)

        try:
            self.ami_client.login(
                username=self.ami_username, secret=self.ami_password)
            self.connected = True
            self.logger.info("Successfully logged into AMI")
            return True

        except Exception as e:

            error = self.handle_ami_exception(e)
            self.logger.error("Unable to login to AMI: %s" % error)

    def logoff(self):

        try:
            self.ami_client.logoff()
            self.connected = True

        except Exception as e:

            error = self.handle_ami_exception(e)
            self.logger.error("Unable to logoff from AMI: %s" % error)

    def send_ping(self):

        self.logger.debug("Sending Ping")
        self.last_ping = time.time()

        try:
            action = SimpleAction('ping')
            self.ami_client.send_action(action)

        except Exception as e:
            error = self.handle_ami_exception(e)
            self.logger.error("Sending Ping Failed: %s" % error)

    def get_channels(self):

        command = ("core show channels concise")

        action = SimpleAction('Command', Command=command)

        try:
            future = self.ami_client.send_action(action)

            response = future.response.follows
            chan_len = len(response) - 1
            response = response[:chan_len]

            self.channels = []

            for channel in response:

                match = re.match(
                    "((.*?)\/.*?)!(.*?)!(.*?)!(.*?)!(.*?)!(.*?)!(.*?)!(.*?)!(.*?)!(.*?)!(.*?)!(.*?)$",
                    channel)

                if match:
                    chan_type = match.group(2)
                    chan = match.group(1)
                    context = match.group(3)
                    extension = match.group(4)
                    priority = match.group(5)
                    state = match.group(6)
                    app = match.group(7)
                    data = match.group(8)
                    clid = match.group(9)
                    duration = match.group(12)
                    bridged_to = match.group(13)

                    parsed_chan = {
                        "chan_type": chan_type,
                        "chan": chan,
                        "context": context,
                        "extension": extension,
                        "priority": priority,
                        "state": state,
                        "app": app,
                        "data": data,
                        "clid": clid,
                        "duration": duration,
                        "bridged_to": bridged_to
                    }

                    self.channels.append(parsed_chan)

                else:
                    self.logger.error("Unable to parse channel: %s " % channel)

            return self.channels

        except Exception as e:
            error = self.handle_ami_exception(e)
            self.logger.error("Unable to get channels: %s" % error)
            self.channels = []

    def handle_ami_exception(self, exception):

        if exception.errno == errno.ECONNREFUSED:
            self.connected = False
            return ("Unable to connect to AMI (Connection Refused)")

        elif exception.errno == errno.EPIPE:
            self.connected = False
            return ("No longer connected to AMI (Broken Pipe)")

        elif exception.errno == errno.EBADF:
            self.connected = False
            return ("No longer connected to AMI (Bad File Descriptor)")

        else:
            self.connected = False
            raise exception

    def check_clients(self):

        for client, params in self.clients.items():

            context = params['context']
            extension = params['extension']
            uri = params['uri']

            if not self.chan_connected(context, extension, uri):
                self.logger.info("Client \'%s\' not connected" % client)
                self.connect_client(client, context, extension, uri)

    def chan_connected(self, context, extension, uri):

        for channel in self.channels:

            if (context == channel['context']
                    and extension == channel['extension']
                    and self.uri_comp(channel['chan'], uri)):

                return True

        return False

    def uri_comp(self, chan_uri, client_uri):

        chan_match = re.match("(.*?)(?:$|-)", chan_uri)

        client_match = re.match("(.*?):(?:.*)@(.*)$", client_uri)

        if chan_match and client_match:

            chan_parsed = chan_match.group(1)

            client_scheme = client_match.group(1).upper()
            client_host = client_match.group(2)

            client_parsed = ("%s/%s" % (client_scheme, client_host))

            # self.logger.debug("Comparing %s and %s" % (client_parsed,
            #                                            chan_parsed))

            if chan_parsed == client_parsed:
                return True

        elif chan_match:

            self.logger.info("Error parsing client URI: %s" % client_uri)
            return False

        elif client_match:

            self.logger.info("Error parsing chan URI: %s" % chan_uri)
            return False

        else:
            self.logger.info("Error parsing client URI: %s" % client_uri)
            self.logger.info("Error parsing chan URI: %s" % chan_uri)
            return False

    def connect_client(self, client, context, extension, uri):

        match = re.match("(.*?):(.*)$", uri)

        if match:

            scheme = match.group(1)
            uri = match.group(2)

            if scheme == "sip":
                scheme = "SIP"
            elif scheme == "iax":
                scheme = "IAX"

            channel = ("%s/%s" % (scheme, uri))

            self.logger.info("Connecting to %s  (%s)" % (client, channel))

            action = SimpleAction(
                'Originate',
                Channel=channel,
                Exten=extension,
                Priority=1,
                Context=context,
                CallerID='AutoDialler', )

            try:
                self.ami_client.send_action(action)
            except Exception as e:
                error = self.handle_ami_exception(e)
                self.logger.info("Unable to connect to %s: %s" % (client,
                                                                  error))

    def run_check(self):

        self.logger.debug("Checking Connected Clients")
        self.last_check = time.time()
        self.last_ping = time.time()
        self.get_channels()
        self.check_clients()

    def reconnect_loop(self):

        self.login()

        if self.connected:
            self.run_check()
            self.last_check = time.time()
            self.last_ping = time.time()

        while not self.kill_received:

            current_time = time.time()

            if not self.connected and current_time - self.last_login > self.reconnect_interval:
                self.logger.info("Reattempting Login")
                self.login()

            elif self.connected:

                if current_time - self.last_check > self.check_interval:
                    self.run_check()

                if current_time - self.last_ping > self.ping_interval:
                    self.send_ping()

            time.sleep(1)

        self.logger.info("Terminating Thread")
        self.logoff()
