#!/usr/bin/env python


########################################################################################################################


class Markdown(object):
    def __init__(self, rows):
        self.rows = rows
        self.widths = {}

    def set_widths(self):
        for row in self.rows:
            for i, col in enumerate(row):
                cur_w = self.widths.get(i, 0)
                new_w = len(str(col).rstrip()) + 2
                if cur_w < new_w:
                    self.widths[i] = new_w

    def get_output(self, *args):
        output = ""
        header_line = ""
        for n, row in enumerate(self.rows):
            for i, col in enumerate(row):
                value = f" {str(col).rstrip()} "

                if n == 0:
                    l = "-" * self.widths[i]
                    header_line += f"|{l: <{self.widths[i]}}"

                if n > 0 and i in args:
                    output += f"|{value: >{self.widths[i]}}"
                else:
                    output += f"|{value: <{self.widths[i]}}"

            output += "|\n"

            if header_line:
                output += f"{header_line}|\n"
                header_line = ""

        return output

