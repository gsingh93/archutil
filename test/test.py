#!/usr/bin/env python

import filecmp
import os
import shutil
import sys
import unittest

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import packages
from packages import DiffResult

class TestInstallFunctions(unittest.TestCase):
    def setUp(self):
        pass


class TestListFunctions(unittest.TestCase):
    def setUp(self):
        pass


class TestConfigFunctions(unittest.TestCase):
    ref_dir = os.path.join(os.getcwd(), 'install_ref_dir')
    test_dir = os.path.join(os.getcwd(), 'test_dir')
    config_dir = os.path.join(test_dir, 'config_files')
    sys_matching_config = os.path.join(test_dir, 'matching')
    bak_matching_config = os.path.join(config_dir, 'matching')
    sys_differing_config = os.path.join(test_dir, 'differing')
    bak_differing_config = os.path.join(config_dir, 'differing')
    sys_only_config = os.path.join(test_dir, 'system_config')
    bak_only_config = os.path.join(config_dir, 'backup_config')
    non_existant_system_config = os.path.join(test_dir, 'backup_config')

    def setUp(self):
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

    def tes_config_diff(self):
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
            result = packages.config_diff(self.config_dir, config_files)[0]
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
        results = packages.config_diff(self.config_dir, config_files)
        packages.install_config_files(results)
        dcmp = filecmp.dircmp(self.test_dir, self.ref_dir)
        assert (len(dcmp.left_only) == 0 and len(dcmp.right_only) == 0
                and len(dcmp.diff_files) == 0)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
