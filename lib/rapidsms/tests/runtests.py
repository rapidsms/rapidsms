#!/usr/bin/python 

from test_component import *
from test_config import*
from test_log import *
from test_message import *
from test_app import *
from test_backend import *
from test_backend_irc import *
from test_backend_spomc import *
from test_router import *
from scripted import MockTestScript

if __name__ == "__main__":
    print "(some tests may pause for a few seconds, this is normal)"
    unittest.main()
