# -*- coding: utf-8 -*-
"""
Run command line interface of PyConcatSRT.
"""

import os
import sys
import argparse


def main():
    sys.path.append('.')

    parser = argparse.ArgumentParser(
                    prog='concatsrt',
                    description='Concatenate SRT files.',
                    epilog='Easy way of concatenate multiples files Srt.'
                )
    parser.add_argument(
        '-p',
        '--path',
        type=str,
        help='set path of file or directory.',
        required=True
    )
    parser.add_argument(
        '-l',
        '--log',
        type=str,
        help='writes a log file with problem files, default = no.'
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        help='final SRT file.'
    )

    args = parser.parse_args()

    path = args.path
    output = args.output
    log = args.log

    if path is not None:
        path_abs = os.path.abspath(path=path)
        if os.path.exists(path_abs):
            write = False
            if log is None:
                write = False
            else:
                if log.lower() == 'yes':
                    write = True
            if output is None:
                output = 'generate_srt.srt'
            else:
                if not output.endswith('.srt'):
                    output += '.srt'

            from src.SrtPyMain import SrtPy
            control = SrtPy()

            if os.path.isfile(path_abs):
                read_data = control.read(path=path_abs)
            elif os.path.isdir(path_abs):
                read_data = control.read_directory(directory_path=path_abs)

            if read_data != []:
                data = control.convertData(data=read_data)
                control.to_write(
                        filename=output,
                        data=data,
                        writeLog=write
                    )

        else:
            print(f'--> {path} <-- not exists.\n')


if __name__ == '__main__':
    main()
