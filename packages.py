#!/usr/bin/env python

import argparse
import os
import re
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


class ListHandler:
    def get_listed_packages(self):
        """Returns a set of packages listed in `listed_packages`"""
        packages = set()
        for v in config.packages.itervalues():
            for s in v:
                packages.add(s)

        return packages

    def get_listed_groups(self, packages):
        """Returns a list of packages in `packages` that are actually groups"""
        command = "pacman -Sg %s | awk '{print $1}' | sort -u" \
                  % " ".join(packages)
        return subprocess.check_output(command, shell=True).rstrip().split('\n')

    def get_installed_packages(self, groups):
        """Returns a set of installed packages"""
        command = ("pacman -Qe | awk '{print $1}' | grep -Fxv -f <(pacman -Qg %s"
                   "| awk '{print $2}')") % " ".join(groups)
        packages = subprocess.check_output(
            command, shell=True, executable="/bin/bash").rstrip().split('\n')
        for i in range(0, len(packages)):
            packages[i] = packages[i].split()[0]
        return set(packages)

    def handle(self, args):
        packages = self.get_listed_packages()
        groups = self.get_listed_groups(packages)
        groups.append('base')
        installed_packages = self.get_installed_packages(groups)

        diff = None
        if not args.inverse:
            # Print all packages that are installed but not listed in the script
            diff = list(installed_packages.difference(packages))
        else:
            # Packages listed in the script but not installed
            diff = list(packages.difference(installed_packages))

        diff.sort()
        print '\n'.join(diff)


class ConfigHandler:
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

    def config_diff(self, config_path, config_files):
        results = []
        for f, system_config_path in config_files.iteritems():
            backup_config_path = os.path.join(config_path, f)
            backup_config_exists = os.path.exists(backup_config_path)
            system_config_exists = os.path.exists(system_config_path)
            if not backup_config_exists or not system_config_exists:
                result = self.DiffResult(
                    backup_config_exists, system_config_exists,
                    self.DiffResult.DOESNT_EXIST, backup_config_path,
                    system_config_path, '')
                results.append(result)
            else:
                p = subprocess.Popen(
                    ['diff', backup_config_path, system_config_path],
                    stdout=subprocess.PIPE)
                diff_output, _ = p.communicate()
                diff_result = (self.DiffResult.MATCHES
                               if p.returncode == 0
                               else self.DiffResult.DIFFERS)
                result = self.DiffResult(
                    backup_config_exists, system_config_exists, diff_result,
                    backup_config_path, system_config_path, diff_output)
                results.append(result)

        assert len(results) == len(config_files)
        return results

    def install_config_files(self, results):
        for r in results:
            if not r.backup_config_exists:
                print_msg(r.backup_config_path + " does not exist", colors.RED)
                continue

            if r.system_config_exists:
                if r.result == self.DiffResult.MATCHES:
                    print_msg("%s and %s match, skipping install"
                              % (r.backup_config_path, r.system_config_path))
                    continue

                assert r.result == self.DiffResult.DIFFERS
                self.safe_copy(r.backup_config_path, r.system_config_path)
            else:
                self.safe_copy(r.backup_config_path, r.system_config_path)

    def update_config_files(self, results):
        for r in results:
            if not r.system_config_exists:
                print_msg(r.system_config_path + " does not exist", colors.RED)
                continue

            if r.backup_config_exists:
                if r.result == self.DiffResult.MATCHES:
                    print_msg("Files match, skipping update of "
                              + r.backup_config_path)
                    continue

                assert r.result == self.DiffResult.DIFFERS

                prompt = ('Update config file with system config '
                          'file (< is config file, > is system '
                          'config file)? [y/N]: ')

                if self.yes_no_choice(prompt, False):
                    self.safe_copy(r.system_config_path,
                                   r.backup_config_path, False)

    def safe_copy(self, path1, path2, safe=True):
        """Safely copies path1 to path2, backing up any file originally at path2
        as path2.bak"""

        def check_all(func, args):
            return all(map(func, args))

        if safe and os.path.exists(path2):
            if not (check_all(os.path.isdir, [path1, path2])
                    or check_all(os.path.isfile, [path1, path2])):
                print_msg(('Both paths must either be only files or only'
                           'directories'), colors.RED)
                return
            self.safe_copy(path2, os.path.normpath(path2) + ".bak")

        print_msg("Copying %s to %s" % (path1, path2), colors.BLUE)
        if os.path.isdir(path1):
            shutil.copytree(path1, path2)
        else:
            assert os.path.isfile(path1)
            shutil.copyfile(path1, path2)

    def yes_no_choice(self, prompt, default_yes):
        yes = set(['yes', 'y', 'ye'])
        no = set(['no','n'])

        if default_yes:
            yes.add('')
        else:
            no.add('')

        while True:
            choice = raw_input(prompt).lower()
            if choice in yes:
                return True
            elif choice in no:
                return False
            else:
                printc("Please respond with 'y' or 'n'", colors.YELLOW)

    def print_diff_results(self, results, output_diff):
        for r in results:
            if r.result == self.DiffResult.DOESNT_EXIST:
                if not r.system_config_exists:
                    print_msg(r.system_config_path + ' does not exist',
                              colors.YELLOW)
                else:
                    assert not r.backup_config_exists
                    print_msg(r.backup_config_path + ' does not exist',
                              colors.YELLOW)
            elif r.result == self.DiffResult.MATCHES:
                print_msg((r.system_config_path +
                           ' matches ' + r.backup_config_path), colors.BLUE)
            else:
                assert r.result == self.DiffResult.DIFFERS
                print_msg((r.system_config_path +
                           ' differs from ' + r.backup_config_path),
                          colors.YELLOW)
                if output_diff:
                    print r.diff_output

    def handle(self, args):
        config_path = args.config_path
        if not os.path.isabs(config_path):
            config_path = os.path.join(os.getcwd(), config_path)

        if not os.path.exists(config_path):
            print_msg("Directory %s does not exist" % config_path, colors.RED)
            return

        results = config_diff(config_path, config.config_files)
        if args.diff:
            self.print_diff_results(results, False)
        elif args.diff_file:
            self.print_diff_results(results, True)
        elif args.install:
            self.install_config_files(results)
        elif args.update:
            self.update_config_files(results)
        else:
            raise ValueError("Argument required for config subcommand")


class InstallHandler:
    def handle(self, args):
        f = open('/etc/pacman.conf').read()
        for repo in config.required_repos:
            if re.search(r'\[%s\]' % repo, f, re.MULTILINE) == None:
                print_msg("Error: %s repository is not enabled" % repo,
                          colors.RED)
                return

        raise NotImplementedError


def parse_arguments():
    parser = argparse.ArgumentParser(description="Package management utility")
    subparsers = parser.add_subparsers(dest='subcommand')

    install_parser = subparsers.add_parser(
        'install', help=('Installs specified package groups'))

    list_parser = subparsers.add_parser(
        'list',
        help="Lists installed packages not already specified in config.py")
    list_parser.add_argument(
        '-i', '--inverse', action='store_true',
        help=('Lists the inverse, i.e. all packages specified in config.py'
              'but not currently installed'))

    config_parser = subparsers.add_parser(
        'config', help="Operations dealing with configuration files")
    config_parser.add_argument(
        '-c', '--config-path',
        help=('Absolute or relative directory path to where configuration files'
              'are stored'), default='config_files')

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


def validate_config_file():
    def check_var_exists(var_name, t):
        if not (hasattr(config, var_name)
                and type(getattr(config, var_name)) == t):
            type_name = t.__name__
            msg = "config.py must contain a %s called `%s`"
            print_msg(msg % (type_name, var_name), colors.RED)
            return False
        return True

    return (check_var_exists('packages', dict)
            and check_var_exists('config_files', dict)
            and check_var_exists('required_repos', list))


def main():
    args = parse_arguments()

    validate_config_file()

    handler = None
    if args.subcommand == 'install':
        handler = InstallHandler()
    elif args.subcommand == 'list':
        handler = ListHandler()
    elif args.subcommand == 'config':
        handler = ConfigHandler()
    else:
        raise ValueError("Invalid subcommand")

    handler.handle(args)

if __name__ == '__main__':
    main()
