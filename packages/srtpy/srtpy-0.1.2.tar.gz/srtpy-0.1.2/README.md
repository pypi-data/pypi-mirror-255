# SrtPy

Automates the tedious task of:

* Correctly formats subtitles.
* Corrects punctuation.
* Takes multiple SRT files to merge them into one file.

By default the final SRT file is named `generated_srt.srt` (using CLI).

> I may add spell check, I am considering it.

# Available commands

* `srtpy` : cli PyConcatSRT
* `srtpy_gui` : gui PyConcatSRT


# Install

```bash
$ pip install srtpy
```

# Usage

* Using CLI.

```bash
$ srtpy [-h] -p PATH [-l LOG] [-o OUTPUT]
```
> PATH : path to file, or directory. Required.

* Using GUI.

```bash
$ srtpy_gui
```
