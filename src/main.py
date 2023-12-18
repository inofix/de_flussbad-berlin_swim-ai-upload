#!/usr/bin/env python3

import sys
import send_html_fiware
import collect_tcp_modbus

# a poor man's argparse alternative
if __name__ == '__main__':
    try:
        if len(sys.argv) == 3:
            if sys.argv[2] == "send":
                send_html_fiware.send_data(sys.argv[1])
            elif sys.argv[2] == "collect":
                collect_tcp_modbus.collect_data(sys.argv[1])
            else:
                print("not implemented, use either 'collect' or 'send'")
        else:
            print("Please provide the name of the config json file and an action")
    except SystemExit:
        sys.exit(1)

