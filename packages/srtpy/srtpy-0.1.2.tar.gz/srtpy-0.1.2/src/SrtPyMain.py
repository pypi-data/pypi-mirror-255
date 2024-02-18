# -*- coding: utf-8 -*-
"""
Class in charge of controlling the information workflow between ReaderSrt,
WriterSrt, ErrorData.
"""

from src.ReaderFileSrt import ReaderSrt
from src.WriterFileSrt import WriterSrt
from src.DialogScript import Dialog
from src.ErrorClass import ErrorData
import os

from typing import Union, List


class SrtPy(object):
    # Controller

    def __init__(self):
        """
        Constructor
        """
        self.path = None
        self.errors_data = []
        self.writer = WriterSrt()
        self.errorData = ErrorData()

    def read(
                self,
                path: str = None
            ) -> Union[List[Dialog], None]:
        """
        Sends `path` to ReaderSrt and returns the processed data sorted by
        start time.
        """
        if path is not None:
            try:
                reader = ReaderSrt(path, self.errorData)
                result_data = reader.process()
                return self.sort_by_timestamp(result_data)
            except FileNotFoundError as e:
                return None

    def read_directory(
        self,
        directory_path: str
    ) -> list:
        """
        """
        path_dir = os.path.abspath(path=directory_path)
        try:
            result_data = []
            for file in os.listdir(path=path_dir):
                file_path = os.path.join(path_dir, file)
                # print(os.path.exists(file_path), file_path)
                data = self.read(path=file_path)
                if data is not None:
                    result_data += data
            return self.sort_by_timestamp(listLineObj=result_data)
        except FileNotFoundError as e:
            print('File "%s" not Found' % os.path.basename(file_path))

    def sort_by_timestamp(
        self,
        listLineObj: list
    ) -> list:
        """
        Returns the list of `Dialog` objects sorted by start timestamp.
        """
        if listLineObj == []:
            return []
        return sorted(
                listLineObj,
                key=lambda x: x.getTimestamps()['start']
            )

    def to_write(
        self,
        filename: str,
        data: str = None,
        writeLog: bool = False
    ) -> Union[bool, None]:
        """
        Writes "data" if not empty, optionally writes the generated error log.
        """
        if writeLog:
            self.write_log()
        if data != "" and data is not None:
            if not filename.endswith('.srt'):
                filename = filename + '.srt'
            self.writer.write(filename, data)
            return True
        else:
            print('>> The data is empty. File has not been written.\n')
            return None

    def write_log(self):
        """
        Writes errors to the log file.
        """
        self.errorData.writeLog()

    def convertData(
        self,
        data: list = None
    ) -> Union[str, None]:
        """
        Converts the list of `Dialog` objects to SRT format and returns it
        in `str`.
        """
        if data != "":
            return self.writer.convertData(data)
        else:
            print('>> The data is empty.\n')
            return None
