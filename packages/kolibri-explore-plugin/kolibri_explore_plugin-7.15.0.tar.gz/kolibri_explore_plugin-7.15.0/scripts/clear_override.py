#!/usr/bin/env python
# Copyright 2021 Endless OS Foundation LLC
# SPDX-License-Identifier: GPL-2.0-or-later
import argparse

from _common import set_channel_override

parser = argparse.ArgumentParser(
    description="Set the channel override to default.",
)
parser.parse_args()
set_channel_override()
