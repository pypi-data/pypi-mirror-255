NAME

::

    OPD - original programmer daemon

SYNOPSIS::

    opd
    opd -c
    opd <cmd> [key=val] 
    opd <cmd> [key==val]

DESCRIPTION::

    OPD is a python3 library implementing the 'opd' package. It
    provides all the tools to program a bot, such as disk perisistence
    for configuration files, event handler to handle the client/server
    connection, code to introspect modules for commands, deferred
    exception handling to not crash on an error, a parser to parse
    commandline options and values, etc.

    OPD provides a demo bot, it can connect to IRC, fetch and
    display RSS feeds, take todo notes, keep a shopping list
    and log text. You can also copy/paste the service file and run
    it under systemd for 24/7 presence in a IRC channel.

    OPD is Public Domain.

INSTALL::

    $ pipx install opd

USAGE::

    without any argument the program does nothing

    $ opd
    $

    provding a command it will run a cli

    $ opd cmd
    cmd,err,mod,req,thr,ver
    $

    the -c option starts a console

    $ opd -c
    >

    the -v option turns on verbose    

    $ opd -cv
    OPD CV started Sat Feb 10 13:50:56 2024
    > 

    use mod= to load additional modules

    $ opd mod=rss
    $

    the ``mod`` command shows a list of modules

    $ opd mod
    cmd,err,fnd,irc,log,mod,req,rss,tdo,thr
    $

    the -a option will load all available modules

    $ opd -a rss
    $

    to start opd in daemon mode use the '-d' option.

    $ opd -d
    $

CONFIGURATION::

    irc

    $ opd cfg server=<server>
    $ opd cfg channel=<channel>
    $ opd cfg nick=<nick>

    sasl

    $ opd pwd <nsvnick> <nspass>
    $ opd cfg password=<frompwd>

    rss

    $ opd rss <url>
    $ opd dpl <url> <item1,item2>
    $ opd rem <url>
    $ opd nme <url< <name>

COMMANDS::

    cmd - commands
    cfg - irc configuration
    dlt - remove a user
    dpl - sets display items
    fnd - find objects 
    log - log some text
    met - add a user
    mre - displays cached output
    pwd - sasl nickserv name/pass
    rem - removes a rss feed
    req - reconsider
    rss - add a feed
    thr - show the running threads

SYSTEMD::

    save the following it in /etc/systemd/system/opd.service and
    replace "<user>" with the user running pipx

    [Unit]
    Description=original programmer daemon
    Requires=network.target
    After=network.target

    [Service]
    Type=simple
    User=<user>
    Group=<user>
    WorkingDirectory=/home/<user>/.opd
    ExecStart=/home/<user>/.local/pipx/venvs/lopd/bin/opd -d
    RemainAfterExit=yes

    [Install]
    WantedBy=multi-user.target

    then run this

    $ mkdir ~/.opd
    $ sudo systemctl enable opd --now

    default channel/server is #opd on localhost

FILES::

    ~/.opd
    ~/.local/bin/opd
    ~/.local/pipx/venvs/opd/


AUTHOR::

    Bart Thate <bthate@dds.nl>


COPYRIGHT::

    OPD is Public Domain.
