# -*- coding: utf-8 -*-
"""
Class in charge of reading the srt file or directory that contains multiple srt
files, returning a list of Dialog objects ordered by start time.
"""

import chardet

import re
import os
from typing import Union, List

from src.ErrorClass import ErrorData
from src.DialogScript import Dialog
from src.CheckerSrtFormat import CheckerSrt
from src.CorrectorTool import Corrector


class ReaderSrt(object):
    """
    Class to read and process files SRT.
    """

    def __init__(
        self,
        path: str = None,
        errordata: object = None
    ) -> None:
        """
        Constructor
        """
        if errordata is not None:
            self.errorData = errordata
        else:
            self.errorData = ErrorData()

        self.path = path
        self.current = 0
        self.corrector = Corrector()

    def process(self) -> List[Dialog]:
        """
        Checks if the path exists and initializes the SRT file(s) workflow.
        Returns list of `Dialog` objects.
        """
        if os.path.exists(self.path):
            return self.__inner_process()
        else:
            raise FileNotFoundError('File or directory not exists.')

    def __inner_process(self) -> List[Dialog]:
        """
        Core method of `process()`, checks if file or directory, returns list
        of `Dialog` objects.
        """
        result_lines = self.read_file(self.path)
        current_filename = result_lines['file']
        lines_objs = self.__iterate_lines(
                                current_filename,
                                result_lines['data']
                            )

        return lines_objs

    def __update_timestamp(
        self,
        list_Dialog: List[Dialog],
        objLastDialog: Dialog
    ) -> list:
        """
        Iterates list and update times start and end of object `Dialog`, return
        list of object `Dialog`.
        """
        last_entry = objLastDialog
        for item in list_Dialog:
            last_entry = item.update_time(last_entry)
        return list_Dialog

    def __iterate_lines(self, filename: str, data: list) -> List[Dialog]:
        """
        Iterates the list elements and returns the list from the `Dialog`,
        logs errors in `ErrorData`.
        """
        list_dialogsOBJ = []
        error_list = []
        total_lines = len(data)
        for i in range(total_lines):
            line = data[i]
            if '-->' in line:
                regex = self.get_timestamps(line)
                if regex is None:
                    error_list.append(self.getIndex(i, data))
                elif regex != []:
                    time_list = regex[0]
                    if CheckerSrt.validate_timestamp(time_list):
                        self.current = self.getIndex(i, data)

# TODO:
                        # Cambiar lista por string separados por `\n`.
                        lineDialogs = self.getLines(i + 1, data)
                        #
# TODO:

                        #
                        # Dialog object
                        #
                        if lineDialogs != []:
                            dialogOBJ = Dialog(
                                        time_start=time_list[0],
                                        time_end=time_list[1]
                                    )
                            dialogOBJ.setPosition(self.getIndex(i, data))

                            res_lines = self.corrector.clear(
                                            list_lines=lineDialogs
                                        )
                            # print(res_lines)

                            dialogOBJ.setDialogs(list_dialog=res_lines)

                            list_dialogsOBJ.append(dialogOBJ)
                        #
                        # Dialog object
                        #
                        else:
                            self.errorData.registerIndex(
                                            filename,
                                            self.getIndex(i, data)
                                        )
                            self.errorData.registerLine(
                                            filename,
                                            i
                                        )
                    else:
                        self.errorData.registerIndex(
                                        filename,
                                        self.getIndex(i, data)
                                    )
                        self.errorData.registerLine(
                                        filename,
                                        i
                                    )

        return self.__sort_timestamp(list_dialogsOBJ)

    def __sort_timestamp(self, listLineObj: list) -> list:
        """
        Returns the list of `Dialog` objects sorted by start timestamp.
        """
        return sorted(
                listLineObj,
                key=lambda x: x.getTimestamps()['start']
            )

    def getEncoding(self, filename) -> dict:
        """
        Return encoding from file SRT.
        """
        with open(filename, 'rb') as file:
            return chardet.detect(file.read())

    def __read(self, filename, encoding) -> list:
        """
        Read method and return all lines from file.
        """
        with open(filename, 'r', encoding=encoding) as file:
            return file.readlines()

    def read_file(self, filename) -> dict:
        """
        Read file SRT.
        """
        file_encoding = self.getEncoding(filename)['encoding']
        data = {
            'file': os.path.basename(filename),
            'data': self.__read(filename, file_encoding)
        }
        return data

    def read_files(self, filename) -> Union[list, None]:
        """
        Read files from the given directory, alphanumeric order,
        SRT files only.
        Maximum 2 discs, 2 files SRT.
        """
        result = []
        files = sorted(os.listdir(filename))
        files = [i for i in files if i.endswith('.srt')]
        if len(files) > 0:
            for item in files[:2]:
                file_path = self.path + f'/{item}'
                if os.path.exists(file_path):
                    file_encoding = self.getEncoding(file_path)['encoding']
                    data = {
                        'file': item,
                        'data': self.__read(file_path, file_encoding)
                    }
                    result.append(data)
            return result
        else:
            return None

    def getIndex(self, current_index, data: list) -> int:
        """
        Return index SRT from file.
        """
        indx = data[current_index - 1].strip()
        if indx.isnumeric():
            return int(indx)
        else:
            return -1

    def getLines(self, current_index, data: list) -> list:
        """
        Returns list of strings of dialog lines from the SRT file.
        """
        # Cambiar lista por un string unidos por `\n`.
        list_dialog = []
        for i in range(current_index, len(data)):
            if data[i].strip() != "":
                list_dialog.append(data[i].strip())
            else:
                break
        return list_dialog

    def get_timestamps(self, line) -> Union[list, None]:
        """
        Return times from SRT file, using Regex to get its.
        Return list of strings `['time_start', 'time_end']` or None.
        """
        reg = r'(\d+:\d{2}:\d{2}\,\d{3}) --> (\d+:\d{2}:\d{2}\,\d{3})'
        regex = re.findall(reg, line)
        if regex != []:
            return regex
        else:
            return None
