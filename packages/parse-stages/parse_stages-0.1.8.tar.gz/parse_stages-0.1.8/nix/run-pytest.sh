#!/bin/sh
#
# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

set -e

: "${PY_MINVER_MIN:=8}"
: "${PY_MINVER_MAX:=12}"

for minor in $(seq -- "$PY_MINVER_MIN" "$PY_MINVER_MAX"); do
	pyver="3$minor"
	nix/cleanpy.sh
	printf -- '\n===== Running tests for %s\n\n\n' "$pyver"
	nix-shell --pure --arg py-ver "$pyver" nix/python-pytest.nix
	printf -- '\n===== Done with %s\n\n' "$pyver"
done
