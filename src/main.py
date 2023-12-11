import sys
import send_html_fiware

# a poor man's argparse alternative
if __name__ == '__main__':
    try:
        if len(sys.argv) == 3:
            if sys.argv[2] == "send":
                send_html_fiware.send_data(sys.argv[1])
            elif sys.argv[2] == "collect":
                print("noop yet")
            else:
                print("not implemented, use either 'collect' or 'send'")
        else:
            print("Please provide the name of the config json file")
    except SystemExit:
        sys.exit(1)
    except Exception as e:
        print("This error was not catched before (what a shame for that programmer): ", e)


