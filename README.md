# de\_flussbad-berlin\_swim-ai-upload

This is a quick way to upload modbus sensor data to a machine learning hub connected by a broker.

## Project Requirements

Create a proof-of-concept solution to integrate [an already running script](https://github.com/RoteKekse/WasserData/) and send the/some data to a FIWARE broker connected to [swim-ai](https://github.com/wseis/swim-ai).


## Prerequisites

  * Python >3.6 (respect order of maps; tested with 3.9.2)
  * pip with virtualenv installed
  * Modbus-TCP source
  * Fiware target

## Get started

In order to get things running, you can e.g. create a virtual environment to separate the software from other applications.
Just clone this repository, change into it. Next you need to copy the
`example_config.json` and adopt it to your needs.
The following commands, executed inside this projects work directory,
set up your environement:

```sh
$ python -m venv venv
$ pip install -r requirements.txt
```
Now you can test the main script with e.g.:

```sh
$ ./src/main.py
```



