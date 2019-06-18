#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""These functions return information about the version of ISIS.
"""

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

import collections
import datetime
import os
import re
from pathlib import Path

from kalasiris import environ

ISISversion = collections.named_tuple('ISISVersion', ['major', 'minor',
                                                      'patch',
                                                      'releaselevel',
                                                      'date'])

version_re = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)")
date_re = re.compile(r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})|(?P<month>\d{1,2})-(?P<day>\d{1,2})-(?P<year>\d{4})")
level_re = re.compile(r"^alpha|beta|stable")


def version_info() -> ISISversion:
    '''Returned named tuple of ISIS version information.'''
    return get_from_file(Path(environ['ISISROOT']) / 'version')


def get_from_file(file_path: os.PathLike) -> ISISversion:
    '''Read an ISIS version file and parse the contents.

       This should parse version files as far back as ISIS 3.5.2.0,
       but possibly earlier.  It will return None values for releaselevel
       and date if it cannot parse them.  It will raise a ValueError if it
       cannot parse a version number.
    '''

    v_text = Path(file_path).read_text

    match = version_re.search(v_text)
    if match:
        version_parsed = match.groupdict()
    else:
        raise ValueError('{} did not match version regex: {}'.format(v_text,
                                                                     version_re.pattern))

    d_match = date_re.search(v_text)
    if d_match:
        d = match.groupdict()
        date = datetime.date(d['year'], d['month'], d['day'])
    else:
        date = None

    l_match = level_re.search(v_text)
    if l_match:
        level = l_match.group
    else:
        level = None

    v = ISISversion(major=version_parsed['major'],
                    minor=version_parsed['minor'],
                    patch=version_parsed['patch'],
                    releaselevel=level,
                    date=date)
    return v
