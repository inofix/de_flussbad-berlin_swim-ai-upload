# de\_flussbad-berlin\_swim-ai-upload

Quick (and dirty) way to upload modbus sensor data to a machine learning hub connected by a broker.

## Project Requirements

Create a proof-of-concept solution to integrate [an already running script](https://github.com/RoteKekse/WasserData/) and send the/some data to a FIWARE broker.


## Prerequisites

  * Python >3.4 (tested with 3.9.2) and pip installed.
  * Modbus-TCP source
  * Fiware target

## Get started

In order to get things running, you can e.g. create a virtual environment to separate the software from other applications.
Just clone this repository, change into it and state the following commands:


```sh
$ python -m venv venv
$ pip install -r requirements.txt
```




