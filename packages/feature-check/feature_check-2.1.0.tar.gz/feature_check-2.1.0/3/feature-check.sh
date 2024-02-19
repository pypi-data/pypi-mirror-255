#!/bin/sh
#
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause


env PYTHONPATH="$(dirname -- "$(dirname -- "$0")")/src${PYTHONPATH+:${PYTHONPATH}}" \
    python3 -m feature_check "$@"
