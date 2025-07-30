"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port", type=int, default=5005, help="The port to listen on")
  args = parser.parse_args()

  # set the handlers
  dispatcher = Dispatcher()
  dispatcher.map("/*", print)
  #dispatcher.map("/volume", print_volume_handler, "Volume")
  #dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

  # start the server
  server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
  print("Serving on {}".format(server.server_address))
  server.serve_forever()