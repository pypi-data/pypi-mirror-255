# -*- coding: utf-8 -*-
"""
Class is responsible for cleaning and formatting the dialogue.
"""

from typing import List
import re


class Corrector:
    """
    Corrects punctuation errors, dialog text alignment.
    """

    def clear(
        self,
        list_lines: List[str]
    ) -> list:
        """
        Main, routes the workflow according to the type of subtitle format.
        """
        list_cleared = []
        for line in list_lines:
            if line.startswith('<font'):
                new_line = self.reformat_w_less_than(line_dialog=line)
            elif line.startswith('{\\an'):
                new_line = self.reformat_tag_bracket(line_dialog=line)
            else:
                new_line = self.reformat_wo_tag(line_dialog=line)
            new_line = self.clear_space_puntuation(line_dialog=new_line)
            new_line = self.fix_exclamation_marks(line_dialog=new_line)
            list_cleared.append(new_line)
        return list_cleared

    def reformat_tag_bracket(
        self,
        line_dialog: str
    ) -> str:
        """
        Corrects formatting to subtitles beginning with `{\anX}`.
        """
        matches = re.search(r'(-\s*.*?[\.|\!|\?]?)\s*-\s*(.*)', line_dialog)
        if matches is not None:
            pos = matches.span()
            line = line_dialog[pos[0]:pos[1] - 1]
            line = self.reformat_wo_tag(line_dialog=line)
            return line_dialog[:pos[0]] + line + line_dialog[pos[1]:]
        else:
            return line_dialog

    def reformat_w_less_than(
        self,
        line_dialog: str
    ) -> str:
        """
        Corrects the formatting of subtitles that use `<tag></tag>` formatting.
        """
        matches = re.search(r'(\-( )?.*?(?<=<))', line_dialog)
        if matches is not None:
            pos = matches.span()
            line = line_dialog[pos[0]:pos[1] - 1]
            line = self.reformat_wo_tag(line_dialog=line)
            return line_dialog[:pos[0]] + line + line_dialog[pos[1]:]
        else:
            return line_dialog

    def reformat_wo_tag(
        self,
        line_dialog: str
    ) -> str:
        """
        Corrects the formatting of dialogs leaving each one on one line.
        """
        r = re.findall(r'(^-\s*.*?[\.|\!|\?]?)\s*-\s*(.*)', line_dialog)
        if r != []:
            l1 = f"- {r[0][0].replace('-', '').strip()}\n"
            l2 = f"- {r[0][1].replace('-', '').strip()}"
            line = l1 + l2
            return line
        else:
            return line_dialog

    def clear_space_puntuation(
        self,
        line_dialog: str
    ) -> str:
        """
        Remove unnecessary spaces between exclamation and question marks.
        """
        line_dialog = line_dialog.replace('¡ ', '¡')
        line_dialog = line_dialog.replace(' !', '!')
        line_dialog = line_dialog.replace('¿ ', '¿')
        line_dialog = line_dialog.replace(' ?', '?')
        return line_dialog

    def fix_exclamation_marks(
        self,
        line_dialog: str
    ) -> str:
        """
        Corrects exclamation errors.
        """
        res = []
        matches = re.search(r'((i|I)?\w+.*[\!]$)', line_dialog, re.DOTALL)
        if matches is not None:
            pos = matches.span()
            item = line_dialog[pos[0]: pos[1]]
            for it in item.split(" "):
                if it.startswith('i'):
                    it = it.replace('i', '¡', 1)
                elif it.startswith('I'):
                    it = it.replace('I', '¡', 1)
                res.append(it)
            return " ".join(res)
        else:
            return line_dialog
