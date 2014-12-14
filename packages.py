#!/usr/bin/env python

import argparse
import os
import subprocess
import shutil
import config

class colors:
    RED     = '\033[31m'
    BLUE    = '\033[34m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    DEFAULT = '\033[0m'


def printc(m, c):
    print c + m + colors.DEFAULT


def print_msg(m, color=colors.DEFAULT):
    printc("========== %s ==========" % m, color)


def get_listed_packages():
    """Returns a set of packages listed in `listed_packages`"""
    packages = set()
    for v in config.packages.itervalues():
        for s in v:
            packages.add(s)

    return packages


def get_listed_groups(packages):
    """Returns a list of packages in `packages` that are actually groups"""
    command = "pacman -Sg %s | awk '{print $1}' | sort -u" % " ".join(packages)
    return subprocess.check_output(command, shell=True).rstrip().split('\n')


def get_installed_packages(groups):
    """Returns a set of installed packages"""
    command = "pacman -Qe | awk '{print $1}' | grep -Fxv -f <(pacman -Qg %s | awk '{print $2}')" % " ".join(groups)
    packages = subprocess.check_output(command, shell=True, executable="/bin/bash").rstrip().split('\n')
    for i in range(0, len(packages)):
        packages[i] = packages[i].split()[0]
    return set(packages)


def check_exists(repo_path, system_path):
    if not os.path.exists(repo_path):
        print_msg(repo_path + " does not exist", colors.RED)
    elif not os.path.exists(system_path):
        print_msg(system_path + " does not exist", colors.YELLOW)
    else:
        return True

    return False


def config_diff(output, config_path):
    out_file = None
    if output == False:
        out_file = open(os.devnull, 'w')

    for f, system_config_file_path in config.config_files.iteritems():
        repo_config_file_path = os.path.join(config_path, f)
        if check_exists(repo_config_file_path, system_config_file_path):
            retcode = subprocess.call(['diff', repo_config_file_path,
                                       system_config_file_path],
                                      stdout=out_file)
            if retcode == 0:
                print_msg(f + " matches", colors.BLUE)
            else:
                print_msg(f + " differs", colors.YELLOW)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Package management utility")
    subparsers = parser.add_subparsers(dest='subcommand')

    install_parser = subparsers.add_parser('install',
                                           help="Installs specified package groups")

    list_parser = subparsers.add_parser('list',
                                        help="Lists installed packages not already specified in config.py")
    list_parser.add_argument('-i', '--inverse', action='store_true',
                             help="Lists the inverse, i.e. all packages specified in config.py but not currently installed")

    config_parser = subparsers.add_parser('config',
                                           help="Operations dealing with configuration files")
    config_parser.add_argument('-c', '--config-path',
                               help="Absolute or relative directory path to where configuration files are stored",
                               default='config_files')

    group = config_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--diff', action='store_true',
                               help="Display filenames of differing files.")
    group.add_argument('-dd', '--diff-file', action='store_true',
                               help="Display file differences.")
    group.add_argument('-i', '--install', action='store_true',
                               help="Install config files on system")
    group.add_argument('-u', '--update', action='store_true',
                               help="Update config files in repo")

    return parser.parse_args()


def handle_install(args):
    if not check_var_exists('packages'):
        return

    raise NotImplementedError


def check_all(func, args):
    return all(map(func, args))


def safe_copy(path1, path2):
    """Safely copies path1 to path2, backing up any file originally at path2 as
    path2.bak"""
    if os.path.exists(path2):
        if not (check_all(os.path.isdir, [path1, path2]) or check_all(os.path.isfile, [path1, path2])):
            print_msg("Both paths must either be only files or only directories", colors.RED)
            return
        safe_copy(path2, os.path.normpath(path2) + ".bak")

    if os.path.isdir(path1):
        shutil.copytree(path1, path2)
    else:
        assert os.path.isfile(path1)
        shutil.copyfile(path1, path2)


def check_var_exists(var_name):
    if not (hasattr(config, var_name) and type(config.config_files) == dict):
        print_msg("config.py must contain a dictionary called `%s`" % var_name,
                  colors.RED)
        return False
    return True

def handle_config(args):
    if not check_var_exists('config_files'):
        return

    config_path = args.config_path
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.getcwd(), config_path)

    if not os.path.exists(config_path):
        print_msg("Directory %s does not exist" % config_path, colors.RED)
        return

    if args.diff:
        config_diff(False, config_path)
    elif args.diff_file:
        config_diff(True, config_path)
    elif args.install:
        for f, path in config.config_files.iteritems():
            repo_config_file_path = os.path.join(config_path, f)
            if not os.path.exists(repo_path):
                print_msg(repo_path + " does not exist", colors.RED)
            else:
                safe_copy(repo_config_file_path, system_config_file_path)
    elif args.update:
        pass
    else:
        raise ValueError("Argument required for config subcommand")


def handle_list(args):
    if not check_var_exists('packages'):
        return

    packages = get_listed_packages()
    groups = get_listed_groups(packages)
    groups.append('base')
    installed_packages = get_installed_packages(groups)

    diff = None
    if not args.inverse:
        # Print all packages that are installed but not listed in the script
        diff = list(installed_packages.difference(packages))
    else:
        # Packages listed in the script but not installed
        diff = list(packages.difference(installed_packages))

    diff.sort()
    print '\n'.join(diff)


def main():
    args = parse_arguments()

    if args.subcommand == 'install':
        handle_install(args)
    elif args.subcommand == 'list':
        handle_list(args)
    elif args.subcommand == 'config':
        handle_config(args)
    else:
        raise ValueError("Invalid subcommand")


if __name__ == '__main__':
    main()
