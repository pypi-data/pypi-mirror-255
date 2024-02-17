{banner}

setux "usage" | "config"
setux [Target] [Command | Action | Module | Manager] [*args | **kwargs]
setux help [Command | Action | Module | Manager]
setux "commands" | "actions" | "modules" | "managers" [pattern]

Deploy Module, Call Manager or Execute Command or Action on Target


"usage":
    Print this.

"config":
    Edit Setux Config


Target:
    May be set:
        - On the command line as the first arg
        - In the environement as "setux_target"
        - In the config dict as the "target" key
    defaults to "local"


Module:
    - Deploy Module ( see the "modules" command )
        ex:
            deploy infos

Manager:
    - Call Manager ( see the "managers" command)
        ex :
            pip installed

    - Get or Set Manager's Property
        ex :
            system hostname
            system hostname:server

Command:
    - Execute Command ( see the "commands" command )
        ex:
            sh ps -ef
            edit /etc/hostname

Action:
    - Execute Action ( see the "actions" command )
        ex:
            Downloader url dest

help:
    - Show help on Acion | Command | Module | Manager
        ex:
            help infos
            help sh

    - Without argument:
        Show usage in the default pager.

"commands" | "actions" | "modules" | "managers"
    - List available commands, actions, modules or managers [filtered by pattern]
        ex:
            actions
            commads list
            modules user

 = = Note = =
    Modules and Actions, as well as system, Package and Service managers may be shortcut
        ex:
            infos           <> deploy infos
            install vim     <> Package install vim
            restart ssh     <> Service restart ssh
            hostname        <> system hostname
            hostname:server <> system hostname:server
            Pinger          <> action Pinger

 = = Note = =
    if not specified :
        enter REPL on Target
