#  Copyright (c) 2021 Dafne-Imaging Team
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  This program was supported by SNF Grant CRSK-3_196515

import sys
from PyQt6.QtWidgets import QApplication
import GenericInputDialog

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(True)

accepted, values = GenericInputDialog.show_dialog("Test", [GenericInputDialog.TextLineInput('Text input'),
                                                           GenericInputDialog.IntSpinInput('My Int', 10, -100, 100),
                                                           GenericInputDialog.FloatSpinInput('My Float'),
                                                           GenericInputDialog.IntSliderInput('My slider'),
                                                           GenericInputDialog.BooleanInput('Bool value'),
                                                           GenericInputDialog.OptionInput('My string options', [
                                                'option 1',
                                                'option 2',
                                                'option 3'
                                            ], 'option 3'),
                                                           GenericInputDialog.OptionInput('My int options', [
                                                            ('option 1', 1.1),
                                                            ('option 2', 2.2),
                                                            ('option 3', 3.3)
                                                        ], 2.2)
                                                           ])
# Note: for option inputs, the value list can be a list of strings, and then the output is the string itself, or a
# list of tuples, where the first element is a string (the label) and the second is the returned value (any).
# The default value for options can be the label string, the default returned value, or an integer index


# returned values can be accessed by key or by position
print(values['My Int'])
print(values[2])

# they can be iterated like a list
for v in values:
    print(v)