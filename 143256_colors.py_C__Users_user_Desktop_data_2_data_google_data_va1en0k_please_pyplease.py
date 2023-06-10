"""Colors!"""

COLORS = {'question': 94,
          'success': 92,
          'warn': 93,
          'failure': 93}

def colored(text, color_type):
    return '\033[{color}m{text}\033[0m'.format(color=COLORS.get(color_type, 0),
                                               text=text)
