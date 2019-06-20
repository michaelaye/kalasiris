#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""These functions return information about the version of ISIS.

    Most of the time, the only thing you'll probably need is the
    version_info() function which returns an ISISversion tuple.
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


class ISISversion(collections.namedtuple('ISISversion',
                                         ['major', 'minor',
                                          'patch', 'releaselevel',
                                          'date'])):
    '''This is a custom collections.namedtuple() which can contain ISIS version
       information.

       The first three elements, major, minor, and patch should be
       integers.  The fourth element, releaselevel, should be the
       string 'alpha', 'beta', or 'stable' or None.  And the fifth
       element, date, should be a datetime.date object or None.
       That's what the functions in this module will return in an ISISversion
       namedtuple.
    '''


version_re = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)")
date_re = re.compile(r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})")
date_yearlast_re = re.compile(r"(?P<month>\d{1,2})-(?P<day>\d{1,2})-(?P<year>\d{4})")  # noqa: E501
level_re = re.compile(r"^alpha|beta|stable")


def version_info() -> ISISversion:
    '''Returned named tuple of ISIS version information for the ISIS system
    underlying kalasiris.  If you want to answer, "What version of ISIS is
    being used?"  This is the function you're after.  It is modeled after
    sys.version_info.'''
    return get_from_file(Path(environ['ISISROOT']) / 'version')


def get_from_string(s: str) -> ISISversion:
    '''Read text and parse the contents for ISIS version information.

       This should parse ISIS version text as far back as ISIS 3.5.2.0,
       but possibly earlier.  It will return None values for releaselevel
       and date if it cannot parse them.  It will raise a ValueError if it
       cannot parse a version number.
    '''

    # Version Matching
    match = version_re.search(s)
    if match:
        v = match.groupdict()
    else:
        raise ValueError(f'{s} did not match version regex: '
                         f'{version_re.pattern}')

    # Date Matching
    d = None
    d_match = date_re.search(s)
    if d_match:
        d = d_match.groupdict()
    else:
        d_match = date_yearlast_re.search(s)
        if d_match:
            d = d_match.groupdict()

    if d is not None:
        date = datetime.date(int(d['year']), int(d['month']), int(d['day']))
    else:
        date = None

    # Level Matching
    level = None
    l_match = level_re.search(s)
    if l_match:
        level = l_match.group()

    version = ISISversion(major=int(v['major']),
                          minor=int(v['minor']),
                          patch=int(v['patch']),
                          releaselevel=level,
                          date=date)
    return version


def get_from_file(file_path: os.PathLike) -> ISISversion:
    '''Read an ISIS version file and parse the contents.

       This should parse version files as far back as ISIS 3.5.2.0,
       but possibly earlier.
    '''

    v_text = Path(file_path).read_text()
    return get_from_string(v_text)