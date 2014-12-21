#!/usr/bin/env python

import filecmp
import os
import shutil
import StringIO
import subprocess
import sys
import unittest

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from packages import ConfigHandler, InstallHandler, ListHandler
DiffResult = ConfigHandler.DiffResult

chroot_message = ('an ArchLinux chroot called "chroot" must be present in the '
                  'test directory. See https://wiki.archlinux.org/index.php/DeveloperWiki:Building_in_a_Clean_Chroot#Setting_Up_A_Chroot '
                  'for more details')
chroot_dir = 'chroot/root'


@unittest.skipIf(not os.path.isdir(chroot_dir), chroot_message)
class TestInstallFunctions(unittest.TestCase):
    def setUp(self):
        assert os.path.isdir(chroot_dir)
        self.cwd = os.getcwd()
        self.real_root = os.open('/', os.O_RDONLY)
        os.chroot(chroot_dir)

    def test_do_install(self):
        install_handler = InstallHandler()
        install_handler.update_repos()

        install_handler.do_install({'all': ['wget']}, ['all'], True)

        assert 'wget' in subprocess.check_output(['pacman', '-Qe'])
        subprocess.check_call(['pacman', '-Rns', 'wget', '--noconfirm'])
        assert 'wget' not in subprocess.check_output(['pacman', '-Qe'])

    def tearDown(self):
        os.fchdir(self.real_root)
        os.chroot('.')
        os.close(self.real_root)
        os.chdir(self.cwd)


@unittest.skipIf(not os.path.isdir(chroot_dir), chroot_message)
class TestListFunctions(unittest.TestCase):
    def setUp(self):
        assert os.path.isdir(chroot_dir)
        self.cwd = os.getcwd()
        self.real_root = os.open('/', os.O_RDONLY)
        os.chroot(chroot_dir)

    def test_list(self):
        list_handler = ListHandler()
        package_list = list_handler.get_installed_packages(['base'])
        assert package_list == set(['flex', 'gcc', 'groff', 'make', 'patch',
                                'automake', 'm4', 'fakeroot', 'bison', 'libtool',
                                'autoconf', 'sudo', 'binutils', 'pkg-config'])

    def tearDown(self):
        os.fchdir(self.real_root)
        os.chroot('.')
        os.close(self.real_root)
        os.chdir(self.cwd)


class TestConfigFunctions(unittest.TestCase):
    install_ref_dir = os.path.join(os.getcwd(), 'install_ref_dir')
    update_ref_dir = os.path.join(os.getcwd(), 'update_ref_dir')
    test_dir = os.path.join(os.getcwd(), 'test_dir')
    config_dir = os.path.join(test_dir, 'config_files')
    sys_matching_config = os.path.join(test_dir, 'matching')
    bak_matching_config = os.path.join(config_dir, 'matching')
    sys_differing_config = os.path.join(test_dir, 'differing')
    bak_differing_config = os.path.join(config_dir, 'differing')
    sys_only_config = os.path.join(test_dir, 'system_config')
    bak_only_config = os.path.join(config_dir, 'backup_config')
    non_existant_system_config = os.path.join(test_dir, 'backup_config')

    config_handler = None

    def assert_dirs_equal(self, dir1, dir2):
        def helper(dcmp):
            assert (len(dcmp.left_only) == 0 and len(dcmp.right_only) == 0
                    and len(dcmp.diff_files) == 0)
            for d in dcmp.subdirs.itervalues():
                helper(d)

        dcmp = filecmp.dircmp(dir1, dir2)
        helper(dcmp)

    def setUp(self):
        self.config_handler = ConfigHandler(self.config_dir)

        assert not os.path.exists(self.test_dir)
        os.makedirs(self.config_dir)

        f = open(self.sys_matching_config, 'w')
        f.write('a')
        f = open(self.bak_matching_config, 'w')
        f.write('a')

        f = open(self.sys_differing_config, 'w')
        f.write('a')
        f = open(self.bak_differing_config, 'w')
        f.write('b')

        open(self.sys_only_config, 'w')
        open(self.bak_only_config, 'w')

    def test_config_diff(self):
        expected_results = [
            DiffResult(True, True, DiffResult.MATCHES, '', '', ''),
            DiffResult(True, True, DiffResult.DIFFERS, '', '',
                       ('1c1\n< b\n\\ No newline at end of file\n---\n>'
                        ' a\n\\ No newline at end of file\n')),
            DiffResult(False, True, DiffResult.DOESNT_EXIST, '', '', ''),
            DiffResult(True, False, DiffResult.DOESNT_EXIST, '', '', '')
        ]

        files = [self.sys_matching_config, self.sys_differing_config,
                 self.sys_only_config, self.non_existant_system_config]

        for f, r in zip(files, expected_results):
            config_files = {os.path.basename(f): f}
            result = self.config_handler.config_diff(self.config_dir, config_files)[0]
            r.backup_config_path = os.path.join(self.config_dir,
                                                os.path.basename(f))
            r.system_config_path = f
            assert result == r

    def test_install_config_files(self):
        config_files = {
            os.path.basename(self.bak_matching_config): self.sys_matching_config,
            os.path.basename(self.bak_differing_config): self.sys_differing_config,
            os.path.basename(self.sys_only_config): self.sys_only_config,
            os.path.basename(self.bak_only_config): self.non_existant_system_config,
        }
        results = self.config_handler.config_diff(self.config_dir, config_files)
        self.config_handler.install_config_files(results)
        self.assert_dirs_equal(self.test_dir, self.install_ref_dir)

    def test_update_config_files(self):
        config_files = {
            os.path.basename(self.bak_matching_config): self.sys_matching_config,
            os.path.basename(self.bak_differing_config): self.sys_differing_config,
            os.path.basename(self.sys_only_config): self.sys_only_config,
            os.path.basename(self.bak_only_config): self.non_existant_system_config,
        }
        results = self.config_handler.config_diff(self.config_dir, config_files)

        old_stdin = sys.stdin
        sys.stdin = StringIO.StringIO('y')
        self.config_handler.update_config_files(results)
        sys.stdin = old_stdin

        self.assert_dirs_equal(self.test_dir, self.update_ref_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main(buffer=True)
