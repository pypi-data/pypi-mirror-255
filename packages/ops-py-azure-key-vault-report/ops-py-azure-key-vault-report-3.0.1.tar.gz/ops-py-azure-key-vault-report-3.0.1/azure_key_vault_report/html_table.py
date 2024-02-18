#!/usr/bin/env python


########################################################################################################################


class HTMLTable(object):
    def __init__(self, table_header):
        self.table_header = table_header
        self.html_table = ""

    def init_html_table(self):
        """generates a html table to be used in json output for MS Teams"""

        self.html_table = f"""<table bordercolor='black' border='2'>
    <thead>
    <tr style='background-color : Teal; color: White'>
"""
        for h in self.table_header:
            self.html_table += f"        <th>{h}</th>\n"

        self.html_table += """
    </tr>
    </thead>
    <tbody>
    """

    def add_html_row(self, *args):
        """adds the table rows to the html table"""

        if not self.html_table:
            return

        self.html_table += "<tr>"
        for arg in args:
            arg = arg.replace(". ", "<br>")
            self.html_table += f"<td>{arg}</td>"
        self.html_table += "</tr>"

    def get_table(self):
        """adding closing html tags and remove plural in days when it should not be used"""

        if self.html_table:
            self.html_table += "</tbody></table>"
            self.html_table = self.html_table.replace(" 1 days", " 1 day").replace("\n", "")
        return self.html_table
