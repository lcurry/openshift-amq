from stomp import *
from datetime import date
import argparse
parser = argparse.ArgumentParser(description='Simple manager for Gitlab Variables')
parser.add_argument('--server_url',help='Pointer to your AMQ Server',default='0.0.0.0')
parser.add_argument('--port',help= 'Port to connect on your AMQ server',default='61613')
parser.add_argument('--queue',help= 'Queue to connect to',default='/queue/test')
args = parser.parse_args()

#Send today's date as a test message
today=date.today().isoformat()
c = Connection([(args.server_url, args.port)])
c.set_listener('stomp_listener', PrintingListener())
c.connect('admin', 'admin', wait=True)
c.send(args.queue, today)