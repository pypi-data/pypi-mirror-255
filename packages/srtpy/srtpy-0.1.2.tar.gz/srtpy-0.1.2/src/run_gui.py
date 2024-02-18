# -*- coding: utf-8 -*-
"""
Run graphics user interface of PyConcatSRT.
"""

import sys


def main():
    from src.GuiPyConcatSRT import main
    main()


if __name__ == '__main__':
    sys.path.append('.')
    main()
