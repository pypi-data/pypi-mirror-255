# This file is placed in the Public Domain.
#
# pylint: disable=C,R,W0401,E0402



""" @KarimKhanQC reconsider OTP-CR-117/19


sbn <cmd> [key=val] [key==val] [mod=n1,n2]
sbn [-a] [-c] [-d] [-h] [-v] [-w]

commands:

cfg - irc configuration
cmd - commands
mod - show available modules
now - show genocide stats
req - reconsider
wsd - show wisdom

options:

-a     load all modules
-c     start console
-d     start daemon
-h     display help
-v     use verbose
-w     wait for services"""


from .defines import *
