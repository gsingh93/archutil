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


def check_var_exists(var_name):
    if not (hasattr(config, var_name) and type(config.config_files) == dict):
        print_msg("config.py must contain a dictionary called `%s`" % var_name,
                  colors.RED)
        return False
    return True


def yes_no_choice(prompt, default_yes):
    yes = set(['yes', 'y', 'ye'])
    no = set(['no','n'])

    if default_yes:
        yes.add('')
    else:
        no.add('')

    choice = raw_input(prompt).lower()
    if choice in yes:
       return True
    elif choice in no:
       return False
    else:
       sys.stdout.write("Please respond with 'y' or 'n'")


def check_all(func, args):
    return all(map(func, args))


def safe_copy(path1, path2, safe=True):
    """Safely copies path1 to path2, backing up any file originally at path2 as
    path2.bak"""
    if safe and os.path.exists(path2):
        if not (check_all(os.path.isdir, [path1, path2]) or check_all(os.path.isfile, [path1, path2])):
            print_msg("Both paths must either be only files or only directories", colors.RED)
            return
        safe_copy(path2, os.path.normpath(path2) + ".bak")

    print_msg("Copying %s to %s" % (path1, path2), colors.BLUE)
    if os.path.isdir(path1):
        shutil.copytree(path1, path2)
    else:
        assert os.path.isfile(path1)
        shutil.copyfile(path1, path2)


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


def check_exists(backup_path, system_path):
    if not os.path.exists(backup_path):
        print_msg(backup_path + " does not exist", colors.RED)
    elif not os.path.exists(system_path):
        print_msg(system_path + " does not exist", colors.YELLOW)
    else:
        return True

    return False


def install_config_files(results):
    for r in results:
        if not r.backup_config_exists:
            print_msg(r.backup_config_path + " does not exist", colors.RED)
        else:
            if r.system_config_exists:
                if r.result == DiffResult.DIFFERS:
                    safe_copy(r.backup_config_path, r.system_config_path)
                else:
                    assert r.result == DiffResult.MATCHES
                    print_msg("%s and %s match, skipping install"
                              % (r.backup_config_path, r.system_config_path))
            else:
                safe_copy(r.backup_config_path, r.system_config_path)


def update_config_files(results):
    for f, system_config_path in config.config_files.iteritems():
        backup_config_path = os.path.join(config_path, f)
        if not os.path.exists(system_config_path):
            print_msg(backup_config_path + " does not exist", colors.RED)
        else:
            if not os.path.exists(backup_config_path):
                safe_copy(system_config_path, backup_config_path)
            else:
                retcode = subprocess.call(['diff', backup_config_path,
                                           system_config_path])
                if retcode != 0:
                    if yes_no_choice("Update config file with system config file (< is config file, > is system config file)? [y/N]: ", False):
                        safe_copy(system_config_path, backup_config_path, False)
                    else:
                        print_msg("Skipping update of file " + f)
                else:
                    print_msg("Files match, skipping update of file " + f)


class DiffResult:
    MATCHES = 'Matches'
    DIFFERS = 'Differs'
    DOESNT_EXIST = "Doesn't exist"

    def __init__(self, backup_config_exists, system_config_exists, result,
                 backup_config_path, system_config_path, diff_output):
        self.backup_config_exists = backup_config_exists
        self.system_config_exists = system_config_exists
        self.result = result
        self.backup_config_path = backup_config_path
        self.system_config_path = system_config_path
        self.diff_output = diff_output

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


def config_diff(config_path, config_files):
    results = []
    for f, system_config_path in config_files.iteritems():
        backup_config_path = os.path.join(config_path, f)
        backup_config_exists = os.path.exists(backup_config_path)
        system_config_exists = os.path.exists(system_config_path)
        if not backup_config_exists or not system_config_exists:
            result = DiffResult(backup_config_exists, system_config_exists,
                                DiffResult.DOESNT_EXIST, backup_config_path,
                                system_config_path, '')
            results.append(result)
        else:
            p = subprocess.Popen(['diff', backup_config_path,
                                  system_config_path],
                                 stdout=subprocess.PIPE)
            diff_output, _ = p.communicate()
            diff_result = (DiffResult.MATCHES
                           if p.returncode == 0 else DiffResult.DIFFERS)
            result = DiffResult(backup_config_exists, system_config_exists,
                                diff_result, backup_config_path,
                                system_config_path, diff_output)
            results.append(result)

    assert len(results) == len(config_files)
    return results


def print_diff_results(results, output_diff):
    for r in results:
        if r.result == DiffResult.DOESNT_EXIST:
            if not r.system_config_exists:
                print_msg(r.system_config_path + ' does not exist',
                          colors.YELLOW)
            else:
                assert not r.backup_config_exists
                print_msg(r.backup_config_path + ' does not exist',
                          colors.YELLOW)
        elif r.result == DiffResult.MATCHES:
            print_msg((r.system_config_path +
                       ' matches ' + r.backup_config_path), colors.BLUE)
        else:
            assert r.result == DiffResult.DIFFERS
            print_msg((r.system_config_path +
                       ' differs from ' + r.backup_config_path),
                      colors.YELLOW)
            if output_diff:
                print r.diff_output


def handle_config(args):
    if not check_var_exists('config_files'):
        return

    config_path = args.config_path
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.getcwd(), config_path)

    if not os.path.exists(config_path):
        print_msg("Directory %s does not exist" % config_path, colors.RED)
        return

    results = config_diff(config_path, config.config_files)
    if args.diff:
        print_diff_results(results, False)
    elif args.diff_file:
        print_diff_results(results, True)
    elif args.install:
        install_config_files(results)
    elif args.update:
        update_config_files(results)
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


def handle_install(args):
    if not check_var_exists('packages'):
        return

    raise NotImplementedError


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
                               help="Update config files in backup folder")

    return parser.parse_args()


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
