#!/usr/bin/env python3
# encoding: utf-8
# ───────────────────────────────── imports ────────────────────────────────── #
import pytest
# ──────────────────────────────────────────────────────────────────────────── #

# ─────────────────────────────── Kernel tests ─────────────────────────────── #
def test_kernel_str():
    d = Dungeon(8, 8)
    print(d)
