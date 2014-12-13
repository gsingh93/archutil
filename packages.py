import subprocess

packages = {'browser': ["google-chrome",
                        "firefox",
                        "flashplayer",
                        "tor-browser-en",
                        "google-talkplugin"],

            'dev': ["boost",
                    "emacs",
                    "docker",
                    "valgrind",
                    "eclipse",
                    "git",
                    "base-devel",
                    "openssh",
                    "gdb",
                    "apache-ant",
                    "jdk7-openjdk",
                    "jdk6",
                    "kcov",
                    "icedtea-web",
                    "abs",
                    "cmake",
                    "nasm",
                    "gcc-multilib",
                    "qemu",
                    "cppcheck",
                    "kdesdk-kcachegrind",
                    "cabal-install",
                    "dart",
                    "go",
                    "terminator",
                    "erlang",
                    "clang",
                    "wine",
                    "maven",
                    "vim",
                    "mit-scheme",
                    "glade",
                    "python2-pillow",
                    "gengetopt",
                    "byacc-noconflict",
                    "mono",
                    "nodejs",
                    "python2-pip",
                    "rust-nightly-bin",
                    "cargo-nightly-bin",
                    "dart-editor",
                    "antlr4",
                    "python2-scipy",
                    "ctags",
                    "rbenv",
                    "ruby-build",
                    "ipython2",
                    "python2-virtualenv",
                    "tmux",
                    "android-sdk",
                    "android-sdk-platform-tools",
                    "android-studio"],

            'gnome': ["gdm",
                      "gnome-terminal",
                      "gnome-control-center",
                      "gnome-keyring",
                      "gnome-tweak-tool",
                      "gtk-engine-murrine",
                      "alacarte",
                      "eog", # Image viewer
                      "evince", # PDF viewer
                      "gnome-media",
                      "file-roller", # Archive manager
                      "gpick",
                      "nautilus",
                      "nautilus-dropbox",
                      "gpaste"],

            'hacking': ["sqlmap-git",
                        "metasploit",
                        "foremost",
                        "bless",
                        "dhex",
                        "nmap",
                        "sslsniff",
                        "ssldump",
                        "burpsuite",
                        "hopper",
                        "fcrackzip",
                        "john",
                        "binwalk",
                        "flasm",
                        "android-apktool",
                        "python2-pcapy",
                        "pylibpcap",
                        "python2-dpkt",
                        "stegdetect",
                        "dex2jar",
                        "pngcheck",
                        "crunch",
                        "fimap-svn",
                        "upx",
                        "jd-gui",
                        "autopsy",
                        "vusb-analyzer",
                        "ltrace",
                        "aircrack-ng-svn", # SVN for -1 patch, might not be necessary anymore
                        "macchanger",
                        "wireshark-gtk",
                        "tcpdump",
                        "whois"],

            'libreoffice': ["libreoffice-fresh-impress",
                            "libreoffice-fresh-writer",
                            "libreoffice-fresh-calc"],

            'misc': ["libisoburn",
                     "shutter",
                     "mtools",
                     "corewars",
                     "httrack",

                     "mlocate",

                     "backintime",
                     "backintime-gnome",
                     "cronie",

                     "tigervnc",
                     "teamviewer",
                     "openvpn",
                     "truecrypt",

                     "aspell-en",

                     "ntfs-3g",
                     "sshfs",
                     "ntp",
                     "gparted",

                     "pkgstats",
                     "hddtemp",
                     "lm_sensors",
                     "cpulimit",

                     # graphics and sound
                     "mesa-libgl",
                     "lib32-mesa-libgl",
                     "lib32-libpulse",
                     "pavucontrol",
                     "lib32-alsa-plugins",

                     # scanners and printers
                     "cups",
                     "hplip",
                     "sane",
                     "brscan",

                     "dia",
                     "fbida",
                     "tk",
                     "ttf-ms-fonts",
                     "mutt",
                     "weechat",
                     "touchegg"],

            'multimedia': ["Bastion",
                           "dvd+rw-tools",
                           "gphoto2",
                           "gphotofs",
                           "handbrake",
                           "vlc",
                           # "steam",
                           # "libtxc_dxtn",
                           # "lib32-libtxc_dxtn",
                           "xboxdrv",
                           "mupen64plus",
                           "dbgl", # Pick one
                           "dosbox",
                           "vbam-gtk",
                           "musescore",
                           "dropbox",
                           #"pcsx2", # PS2 Emulator
                           "lmms",
                           "gimp",
                           "gimp-ufraw",
                           "ffmpeg",
                           "audacity",
                           "kdenlive",
                           "gnome-chess",
                           "gnuchess",
                           "blender",
                           "deluge"],

            'networking': ["wpa_supplicant",
                           "iw",
                           "dialog", # Optional dep for netctl
                           "netctl",
                           "networkmanager",
                           "rfkill"],

            'shell': ["zsh",
                      "oh-my-zsh-git",
                      "lsof",
                      "espeak",
                      "dos2unix",
                      "pkgfile",
                      "strace",
                      "lynx",
                      "bash-completion",
                      "wget",
                      "curl",
                      "p7zip",
                      "tree",
                      "zip",
                      "cowsay",
                      "fortune-mod",
                      "wol",
                      "ascii",
                      "scrot", # Command line screen capture
                      "pdftk",
                      "sdcv", # Command line spell checker
                      "gnu-netcat",
                      "traceroute",
                      "dnsutils",
                      "stardict-wordnet"], # Required for sdcv

            'virtualbox': ["virtualbox",
                           "virtualbox-guest-utils",
                           "virtualbox-guest-iso"],

            'webdev': ["apache",
                       "php",
                       "mariadb",
                       "php-apache",
                       "php-gd", # ?
                       "rsync",
                       "rake"],

            'x11': ["xorg-xinit",
                    "xorg-xbacklight",
                    "xorg-xrandr",
                    "xorg-server-xephyr",
                    "xclip",
                    "xterm"],

            'x11_extra':["xdotool",
                         "xflux",
                         "xorg-xwininfo",
                         "xorg-xev",
                         "xorg-xmodmap",
                         "xbindkeys",
                         "conky-lua",
                         "awesome"]
}

# Get a list of packages in this script
pkg_set = set()
for k, v in packages.iteritems():
    for s in v:
        pkg_set.add(s)

# Get a list of manually installed packages
installed_packages = subprocess.check_output("pacman -Qe | awk '{print $1}' | grep -Fxv -f <(pacman -Qg | awk '{print $2}')", shell=True, executable="/bin/bash").rstrip().split('\n')
tmp = []
for p in installed_packages:
    tmp.append(p.split()[0])
installed_packages = set(tmp)

# Print all packages that are installed but not in the script
diff = list(installed_packages.difference(pkg_set))
diff.sort()
print '\n'.join(diff)

# Packages in my list but not installed (for finding errors)
diff = list(pkg_set.difference(installed_packages))
diff.sort()
print '\n'.join(diff)
