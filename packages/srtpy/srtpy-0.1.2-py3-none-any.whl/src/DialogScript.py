# -*- coding: utf-8 -*-
"""
Class to convert data into a Dialog object such as the start and end time of
the dialog, the dialog lines, the location of the original srt file.
"""


from datetime import datetime, timedelta
from typing import NewType, Dict, List


dialog = NewType('Dialog', object)


class Dialog(object):
    def __init__(self, time_start: str, time_end: str):
        self.line = -1
        self.time_start = time_start
        self.time_end = time_end
        self.dialog = []

    def setPosition(self, line: List[int]) -> None:
        if line > 0:
            self.line = line

    def setDialogs(self, list_dialog: List[str]) -> None:
        if list_dialog != []:
            self.dialog = list_dialog

    def getTimestamps(self) -> Dict[datetime.timestamp, datetime.timestamp]:
        t = self.getDatetimes()
        return {
            'start': t['start'].timestamp(),
            'end': t['end'].timestamp()
        }

    def getDatetimes(self) -> Dict[datetime, datetime]:
        return {
                'start': datetime.strptime(
                            self.time_start, '%H:%M:%S,%f'
                        ),
                'end': datetime.strptime(
                            self.time_end, '%H:%M:%S,%f'
                        )
            }

    def update_time(
        self,
        objDialog: dialog
    ) -> dialog:
        if isinstance(objDialog, Dialog):
            def getDelta(time):
                return timedelta(
                    hours=time.hour,
                    minutes=time.minute,
                    seconds=time.second,
                    microseconds=time.microsecond
                )
            other = objDialog.getDatetimes()
            this = self.getDatetimes()

            # print('-->', other['start'].time(), other['end'].time())
            # print('-->', this['start'].time(), this['end'].time())

            diff_time = this['end'] - this['start']
            date_diff = datetime.strptime(
                        str(diff_time).replace('.', ','),
                        '%H:%M:%S,%f'
                    )
            new_start = (other['end'] + getDelta(date_diff))
            new_end = (new_start + getDelta(date_diff))
            new_start_time = new_start.time()
            new_end_time = new_end.time()
            self.time_start = str(new_start_time).replace('.', ',')[:12]
            self.time_end = str(new_end_time).replace('.', ',')[:12]

            return self

    def __str__(self) -> str:
        return "{0} - {1}, {2} => {3}".format(
                self.line,
                self.time_start,
                self.time_end,
                ' '.join(self.dialog)[:10]
            )
