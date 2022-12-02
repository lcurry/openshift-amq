from stomp import *
import time
import argparse
parser = argparse.ArgumentParser(description='Simple manager for Gitlab Variables')
parser.add_argument('--server_url',help='Pointer to your AMQ Server', default="0.0.0.0")
parser.add_argument('--port',help= 'Port to connect on your AMQ server',default='61613')
parser.add_argument('--queue',help= 'Queue to connect to',default='/queue/test')
args = parser.parse_args()
class CustomListener(ConnectionListener):
    def __init__(self, print_to_log=False):
        self.print_to_log = print_to_log

    def __print(self, msg, *args):
        if self.print_to_log:
            logging.info(msg, *args)
        else:
            print(msg % args)

    def on_connecting(self, host_and_port):
        """
        :param (str,int) host_and_port:
        """
        self.__print("on_connecting %s %s", *host_and_port)
        print("Connecting")

    def on_connected(self, frame):
        """
        :param Frame frame: the stomp frame
        """
        self.__print("on_connected %s %s", frame.headers, frame.body)
        print("Connected")

    def on_disconnected(self):
        self.__print("on_disconnected")

    def on_heartbeat_timeout(self):
        self.__print("on_heartbeat_timeout")

    def on_before_message(self, frame):
        """
        :param Frame frame: the stomp frame
        """
        self.__print("on_before_message %s %s", frame.headers, frame.body)
        print("Receiving")

    def on_message(self, frame):
        """
        :param Frame frame: the stomp frame
        """
        self.__print("on_message %s %s", frame.headers, frame.body)
        print("Received message: "+frame.body)

    def on_receipt(self, frame):
        """
        :param Frame frame: the stomp frame
        """
        self.__print("on_receipt %s %s", frame.headers, frame.body)
        print("Received message: "+frame.body)

    def on_error(self, frame):
        """
        :param Frame frame: the stomp frame
        """
        self.__print("on_error %s %s", frame.headers, frame.body)
        print("Error: "+frame.body)

# Setup the connection object, then connect and subscribe to our queue
c = Connection([(args.server_url, args.port)])
c.set_listener('stomp_listener', CustomListener())
c.connect('admin', 'admin', wait=True)
c.subscribe(args.queue, 123)

# We need a loop to consume messages from the queue and display them in the terminal
print("Queue read loop, ctrl+c to quit")
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    c.disconnect()
    print("Reciever terminated")
