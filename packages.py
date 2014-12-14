#!/usr/bin/env python

import argparse
import os
import subprocess

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


listed_packages = {
    'browser': ["firefox",
                "flashplayer",
                "google-chrome",
                "google-talkplugin",
                "tor-browser-en"],

    'dev': ["abs",
            "android-sdk",
            "android-sdk-platform-tools",
            "android-studio",
            "antlr4",
            "apache-ant",
            "base-devel",
            "boost",
            "byacc-noconflict",
            "cabal-install",
            "cargo-nightly-bin",
            "clang",
            "cmake",
            "cppcheck",
            "ctags",
            "dart",
            "dart-editor",
            "docker",
            "eclipse",
            "emacs",
            "erlang",
            "gcc-multilib",
            "gdb",
            "gengetopt",
            "git",
            "git-number",
            "glade",
            "go",
            "icedtea-web",
            "ipython2",
            "jdk6",
            "jdk7-openjdk",
            "kcov",
            "kdesdk-kcachegrind",
            "maven",
            "mit-scheme",
            "mono",
            "nasm",
            "nodejs",
            "openssh",
            "python2-pillow",
            "python2-pip",
            "python2-scipy",
            "python2-virtualenv",
            "qemu",
            "rbenv",
            "ruby-build",
            "rust-nightly-bin",
            "terminator",
            "tmux",
            "valgrind",
            "vim",
            "wine"],

    'gnome': ["alacarte",
              "eog", # Image viewer
              "evince", # PDF viewer
              "file-roller", # Archive manager
              "gdm",
              "gnome-control-center",
              "gnome-keyring",
              "gnome-media",
              "gnome-terminal",
              "gnome-tweak-tool",
              "gpaste",
              "gpick",
              "gtk-engine-murrine",
              "nautilus",
              "nautilus-dropbox"],

    'hacking': ["aircrack-ng-svn",  # SVN for -1 patch, might not be necessary anymore
                "android-apktool",
                "autopsy",
                "binwalk",
                "bless",
                "burpsuite",
                "crunch",
                "dex2jar",
                "dhex",
                "fcrackzip",
                "fimap-svn",
                "flasm",
                "foremost",
                "hopper",
                "jd-gui",
                "john",
                "ltrace",
                "macchanger",
                "metasploit",
                "nmap",
                "pngcheck",
                "pylibpcap",
                "python2-dpkt",
                "python2-pcapy",
                "sqlmap-git",
                "ssldump",
                "sslsniff",
                "stegdetect",
                "tcpdump",
                "upx",
                "vusb-analyzer",
                "whois",
                "wireshark-gtk"],

    'libreoffice': ["libreoffice-fresh-calc",
                    "libreoffice-fresh-impress",
                    "libreoffice-fresh-writer"],

    'misc': ["aspell-en",
             "backintime",
             "backintime-gnome",
             "brscan",
             "corewars",
             "cpulimit",
             "cronie",
             "cups",
             "dia",
             "fbida",
             "gparted",
             "hddtemp",
             "hplip",
             "httrack",
             "lib32-alsa-plugins",
             "lib32-libpulse",
             "lib32-mesa-libgl",
             "libisoburn",
             "lm_sensors",
             "mesa-libgl",
             "mlocate",
             "mtools",
             "mutt",
             "ntfs-3g",
             "ntp",
             "openvpn",
             "pavucontrol",
             "pkgstats",
             "sane",
             "shutter",
             "sshfs",
             "teamviewer",
             "tigervnc",
             "tk",
             "touchegg",
             "truecrypt",
             "ttf-ms-fonts",
             "weechat"],

    'multimedia': ["Bastion",
                   "audacity",
                   "blender",
                   "dbgl", # TODO: Pick this or dosbox
                   "deluge",
                   "dosbox",
                   "dropbox",
                   "dvd+rw-tools",
                   "ffmpeg",
                   "gimp",
                   "gimp-ufraw",
                   "gnome-chess",
                   "gnuchess",
                   "gphoto2",
                   "gphotofs",
                   "handbrake",
                   "kdenlive",
                   "libtxc_dxtn", # Steam dependency
                   "lib32-libtxc_dxtn", # Steam dependency
                   "lmms",
                   "mupen64plus",
                   "musescore",
                   #"pcsx2", # PS2 Emulator
                   "steam",
                   "vbam-gtk",
                   "vlc",
                   "xboxdrv"],

    'networking': ["dialog", # Optional dep for netctl
                   "iw",
                   "netctl",
                   "networkmanager",
                   "rfkill",
                   "wpa_supplicant"],

    'shell': ["ascii",
              "bash-completion",
              "cowsay",
              "curl",
              "dnsutils",
              "dos2unix",
              "espeak",
              "fortune-mod",
              "gnu-netcat",
              "lsof",
              "lynx",
              "oh-my-zsh-git",
              "p7zip",
              "pdftk",
              "pkgfile",
              "scrot", # Command line screen capture
              "sdcv", # Command line spell checker
              "stardict-wordnet", # Dependency for sdcv
              "strace",
              "traceroute",
              "tree",
              "wget",
              "wol",
              "zip",
              "zsh"],

    'virtualbox': ["virtualbox",
                   "virtualbox-guest-iso",
                   "virtualbox-guest-utils"],

    'webdev': ["apache",
               "mariadb",
               "php",
               "php-apache",
               "php-gd", # TODO: ?
               "rake",
               "rsync"],

    'x11': ["xclip",
            "xorg-server-xephyr",
            "xorg-xbacklight",
            "xorg-xinit",
            "xorg-xrandr",
            "xterm"],

    'x11_extra': ["awesome",
                  "conky-lua",
                  "xbindkeys",
                  "xdotool",
                  "xflux",
                  "xorg-xev",
                  "xorg-xmodmap",
                  "xorg-xwininfo"]
}

config_files = {
    'bashrc': '/home/gulshan/.bashrc',
    'bash_aliases': '/home/gulshan/.bash_aliases',
    'bash_functions': '/home/gulshan/.bash_functions',
    'emacs': '/home/gulshan/.emacs',
    'gdbinit': '/home/gulshan/.gdbinit',
    'gitconfig': '/home/gulshan/.gitconfig',
    'tmux.conf': '/home/gulshan/.tmux.conf',
    'ssh_config': '/home/gulshan/.ssh/config',
}


def get_listed_packages():
    """Returns a set of packages listed in `listed_packages`"""
    packages = set()
    for v in listed_packages.itervalues():
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

def config_diff(output, config_path):
    if not os.path.exists(config_path):
        print_msg("Directory %s does not exist" % config_path, colors.RED)
        return

    out_file = None
    if output == False:
        out_file = open(os.devnull, 'w')

    for f, system_config_file_path in config_files.iteritems():
        repo_config_file_path = os.path.join(config_path, f)
        if not os.path.exists(repo_config_file_path):
            print_msg(repo_config_file_path + " does not exist", colors.RED)
        elif not os.path.exists(system_config_file_path):
            print_msg(system_config_file_path + " does not exist", colors.YELLOW)
        else:
            retcode = subprocess.call(['diff', repo_config_file_path,
                                       system_config_file_path],
                                      stdout=out_file)
            if retcode == 0:
                print_msg(f + " matches", colors.BLUE)
            else:
                print_msg(f + " differs", colors.YELLOW)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Package management utility tool")
    subparsers = parser.add_subparsers(dest='subcommand')

    install_parser = subparsers.add_parser('install',
                                           help="Installs specified package groups")

    list_parser = subparsers.add_parser('list',
                                        help="Lists installed packages not in this listed in this script")
    list_parser.add_argument('-i', '--inverse', action='store_true',
                             help="Lists the inverse, i.e. all packages listed in this script but not currently installed")

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


def main():
    args = parse_arguments()

    if args.subcommand == 'install':
        raise NotImplementedError
    elif args.subcommand == 'list':
        packages = get_listed_packages()
        groups = get_listed_groups(packages)
        groups.append('base')
        installed_packages = get_installed_packages(groups)

        if not args.inverse:
            # Print all packages that are installed but not listed in the script
            diff = list(installed_packages.difference(packages))
            diff.sort()
            print '\n'.join(diff)
        else:
            # Packages listed in the script but not installed
            diff = list(packages.difference(installed_packages))
            diff.sort()
            print '\n'.join(diff)
    elif args.subcommand == 'config':
        config_path = args.config_path
        if not os.path.isabs(config_path):
            config_path = os.path.join(os.getcwd(), config_path)

        if args.diff:
            config_diff(False, config_path)
        elif args.diff_file:
            config_diff(True, config_path)
        elif args.install:
            pass
        elif args.update:
            pass
        else:
            raise ValueError("Argument required for config subcommand")
    else:
        raise ValueError("Invalid subcommand")


if __name__ == '__main__':
    main()
