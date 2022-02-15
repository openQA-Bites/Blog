#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pendulum        # Check poetry by adding at least one dependency

if __name__ == "__main__" :
	now = pendulum.now("Europe/Amsterdam")
	print(now.to_iso8601_string())
	now.in_timezone("America/Toronto")
	print(now.to_iso8601_string())
