#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `kalasiris` package."""

# Copyright 2019, Ross A. Beyer (rbeyer@seti.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import contextlib
import os
import subprocess
import unittest
from unittest.mock import call, patch, Mock
from pathlib import Path

import kalasiris as isis
from .utils import resource_check as rc


# Hardcoding these, but I sure would like a better solution.
# IsisPreferences = os.path.join('test-resources', 'IsisPreferences')
HiRISE_img = Path('test-resources') / 'PSP_010502_2090_RED5_0.img'


class TestResources(unittest.TestCase):
    '''Establishes that the test image exists.'''

    def test_resources(self):
        (truth, test) = rc(HiRISE_img)
        self.assertEqual(truth, test)


class Test_getkey_k(unittest.TestCase):

    def setUp(self):
        self.cub = Path('test_getkey_k.cub')
        isis.hi2isis(HiRISE_img, to=self.cub)

    def tearDown(self):
        self.cub.unlink()
        with contextlib.suppress(FileNotFoundError):
            Path('print.prt').unlink()

    def test_getkey_k(self):
        truth = 'HIRISE'
        key = isis.getkey_k(self.cub, 'Instrument', 'InstrumentId')
        self.assertEqual(truth, key)


class Test_hi2isis_k(unittest.TestCase):

    def setUp(self):
        self.img = HiRISE_img

    def tearDown(self):
        with contextlib.suppress(FileNotFoundError):
            Path('print.prt').unlink()

    def test_with_to(self):
        tocube = Path('test_hi2isis_k.cub')
        isis.hi2isis_k(self.img, to=tocube)
        self.assertTrue(tocube.is_file())
        tocube.unlink()

    def test_without_to(self):
        tocube = Path(self.img).with_suffix('.cub')
        isis.hi2isis_k(self.img)
        self.assertTrue(tocube.is_file())
        tocube.unlink()


class Test_hist_k(unittest.TestCase):

    def setUp(self):
        self.cube = Path('test_hist.cub')
        isis.hi2isis(HiRISE_img, to=self.cube)

    def tearDown(self):
        self.cube.unlink()
        with contextlib.suppress(FileNotFoundError):
            Path('print.prt').unlink()

    def test_run(self):
        hist_as_string = isis.hist_k(self.cube)
        self.assertTrue(hist_as_string.startswith('Cube'))

    def test_run_with_to(self):
        text_file = Path('test_hist.hist')
        hist_as_string = isis.hist_k(self.cube, to=text_file)
        self.assertTrue(text_file.is_file())
        self.assertTrue(hist_as_string.startswith('Cube'))
        text_file.unlink()

    def test_fail(self):
        # ISIS hist_k needs at least a FROM=, giving it nothing:
        self.assertRaises(subprocess.CalledProcessError, isis.hist_k)


class Test_stats_k(unittest.TestCase):

    def setUp(self):
        self.stats_text = '''Group = Results
  From                    = PSP_010502_2090_RED4_1.cub
  Band                    = 1
  Average                 = 6498.477293457
  StandardDeviation       = 181.94624138776
  Variance                = 33104.434755134
  Median                  = 6497.0
  Mode                    = 6534.0
  Skew                    = 0.024358185897602
  Minimum                 = 4117.0
  Maximum                 = 8207.0
  Sum                     = 13308881497.0
  TotalPixels             = 2048000
  ValidPixels             = 2048000
  OverValidMaximumPixels  = 0
  UnderValidMinimumPixels = 0
  NullPixels              = 0
  LisPixels               = 0
  LrsPixels               = 0
  HisPixels               = 0
  HrsPixels               = 0
End_Group
'''

    def test_stats_k(self):
        cp = Mock(stdout=self.stats_text)
        with patch('kalasiris.k_funcs.isis.stats', return_value=cp):
            d = isis.stats_k('foo')
            self.assertEqual(20, len(d))
            self.assertEqual(d['Average'], '6498.477293457')

    @unittest.skip("Tests on a real file.")
    def test_stats_k_file(self):
        cub = Path('test_stats_k.cub')
        isis.hi2isis(HiRISE_img, to=cub)

        d = isis.stats_k(cub)
        self.assertEqual(d['TotalPixels'], '2048000')

        cub.unlink()
        with contextlib.suppress(FileNotFoundError):
            Path('print.prt').unlink()


class Test_cubeit_k(unittest.TestCase):

    @patch('kalasiris.k_funcs.os.unlink')
    @patch('kalasiris.k_funcs.isis.cubeit')
    def test_cubeit_k(self, m_cubeit, m_unlink):
        filelike = Mock()
        filelike.name = 'fromlist.txt'
        with patch('kalasiris.k_funcs.isis.tempfile.NamedTemporaryFile',
                   return_value=filelike):
            isis.cubeit_k(['a.cub', 'b.cub', 'c.cub'], to='stacked.cub')
            self.assertEqual(filelike.mock_calls,
                             [call.write('a.cub'),
                              call.write('\n'),
                              call.write('b.cub'),
                              call.write('\n'),
                              call.write('c.cub'),
                              call.write('\n'),
                              call.write(''),
                              call.write('\n'),
                              call.close()])
            self.assertEqual(m_cubeit.call_args_list,
                             [call(fromlist='fromlist.txt', to='stacked.cub')])

    @unittest.skip("Tests on a real file.")
    def test_cubeit_k_files(self):
        a_cube = 'test_cubeit_a.cub'
        isis.makecube(to=a_cube, value=1, samples=2, lines=2, bands=1)
        b_cube = 'test_cubeit_b.cub'
        isis.makecube(to=b_cube, value=1, samples=2, lines=2, bands=1)
        c_cube = 'test_cubeit_c.cub'
        isis.makecube(to=c_cube, value=1, samples=2, lines=2, bands=1)
        s_cube = 'test_cubeit_stacked.cub'
        isis.cubeit_k([a_cube, b_cube, c_cube], to=s_cube)
        for f in (a_cube, b_cube, c_cube, s_cube):
            os.unlink(f)
        with contextlib.suppress(FileNotFoundError):
            Path('print.prt').unlink()
