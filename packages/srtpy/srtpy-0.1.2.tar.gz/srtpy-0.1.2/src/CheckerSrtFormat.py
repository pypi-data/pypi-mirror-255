# -*- coding: utf-8 -*-
"""
Class in charge of checking the SRT format of times.
"""


from datetime import datetime


class CheckerSrt(object):

    def validate_timestamp(timestamps: list) -> bool:
        """
        Receives a list of timestamp strings in the format
        `["start_time", "end_time"]` from a regex.
        """
        def format(timestamp):
            return timestamp + (15 - len(timestamp)) * '0'

        start = format(timestamps[0])
        end = format(timestamps[1])

        try:
            d1 = datetime.strptime(start, '%H:%M:%S,%f').timestamp()
            d2 = datetime.strptime(end, '%H:%M:%S,%f').timestamp()
            return d2 > d1
        except ValueError as e:
            print('>>>  ', e)
            return False
