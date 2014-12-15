#!/usr/bin/env python

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
    test_dir = os.path.join(os.getcwd(), 'test_dir')
    config_dir = os.path.join(test_dir, 'config_files')
    sys_matching_file = os.path.join(test_dir, 'matching')
    bak_matching_file = os.path.join(config_dir, 'matching')
    sys_differing_file = os.path.join(test_dir, 'differing')
    bak_differing_file = os.path.join(config_dir, 'differing')
    system_only_config = os.path.join(test_dir, 'system_config')
    backup_only_config = os.path.join(config_dir, 'backup_config')
    non_existant_system_config = os.path.join(test_dir, 'backup_config')

    def setUp(self):
        assert not os.path.exists(self.test_dir)
        os.makedirs(self.config_dir)

        f = open(self.sys_matching_file, 'w')
        f.write('a')
        f = open(self.bak_matching_file, 'w')
        f.write('a')

        f = open(self.sys_differing_file, 'w')
        f.write('a')
        f = open(self.bak_differing_file, 'w')
        f.write('b')

        open(self.system_only_config, 'w')
        open(self.backup_only_config, 'w')

    def test_config_diff(self):
        expected_results = [
            DiffResult(True, True, DiffResult.MATCHES, '', '', ''),
            DiffResult(True, True, DiffResult.DIFFERS, '', '',
                       ('1c1\n< b\n\\ No newline at end of file\n---\n>'
                        ' a\n\\ No newline at end of file\n')),
            DiffResult(False, True, DiffResult.DOESNT_EXIST, '', '', ''),
            DiffResult(True, False, DiffResult.DOESNT_EXIST, '', '', '')
        ]
        for f, r in zip([self.sys_matching_file, self.sys_differing_file,
                  self.system_only_config, self.non_existant_system_config],
                     expected_results):
            config_files = {os.path.basename(f): f}
            result = packages.config_diff(self.config_dir, config_files)[0]
            r.backup_config_path = os.path.join(self.config_dir,
                                                os.path.basename(f))
            r.system_config_path = f
            assert result == r

    def tearDown(self):
        shutil.rmtree(self.test_dir)

if __name__ == '__main__':
    unittest.main()
