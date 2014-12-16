Package and Config Backup Utility
=================================

This utility allows you to create a list of explicitly installed packages which you can later use to install those same packages on any machine. This tool also allows you to keep config files in sync between your system and some backup files (a common requirement with version controlled dotfiles, like `.bashrc`). Currently, package listing and installation is only supported on Arch Linux. There are no plans to port this utility to other platforms, but this shouldn't be hard to do, and pull requests are welcome.

Usage
-----

```
$ ./packages.py -h
usage: packages.py [-h] {install,list,config} ...

Package management utility

positional arguments:
  {install,list,config}
    install             Installs specified package groups
    list                Lists installed packages not already specified in
                        config.py
    config              Operations dealing with configuration files

optional arguments:
  -h, --help            show this help message and exit
```

### List Packages

### Install Packages

```
$ ./packages.py list -h
usage: packages.py list [-h] [-i]

optional arguments:
  -h, --help     show this help message and exit
  -i, --inverse  Lists the inverse, i.e. all packages specified in config.py
                 but not currently installed
```

### Config

```
$ ./packages.py config -h
usage: packages.py config [-h] [-c CONFIG_PATH] (-d | -dd | -i | -u)

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_PATH, --config-path CONFIG_PATH
                        Absolute or relative directory path to where
                        configuration files are stored
  -d, --diff            Display filenames of differing files.
  -dd, --diff-file      Display file differences.
  -i, --install         Install config files on system
  -u, --update          Update config files in backup folder
```
