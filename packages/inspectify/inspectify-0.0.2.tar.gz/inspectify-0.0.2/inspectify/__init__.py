import inspect
import os
import re

is_colored_module_imported = True
try: import colored
except: is_colored_module_imported = False

# Make the d() function accessible from any Python script on the local system:
# set --export --universal PYTHONPATH ~/Softwareentwicklung/create_trace

def colored_bg(color):
  if is_colored_module_imported:
    return colored.bg(color)
  else:
    return None

def colored_fg(color):
  if is_colored_module_imported:
    return colored.fg(color)
  else:
    return None

def colored_stylize(text, color):
  if is_colored_module_imported:
    return colored.stylize(text, color)
  else:
    return text

# Just a developer tool: to generate a trace of the Python script,
# that is more detailed than print commands deliver.
def d(value):

  # Get the expression, via which 'value' is brought here.
  # How is the value expressed in the Python language?
  frame = inspect.currentframe()
  expressions = inspect.getframeinfo(frame.f_back).code_context
  line_number = inspect.getframeinfo(frame.f_back).lineno
  expression = expressions[0]
  left_index = expression.find('(') + 1 # jump over the opening parenthesis
  right_index = -2 # the ')\n' symbols are at the last 2 positions of the string
  expression = expression[left_index:right_index]

  print('---------------------------------------------------------------')

  # Show the given expression of the value.
  print(f'''{colored_stylize(expression, colored_fg('green_1'))} at line {colored_stylize(f'{line_number}', colored_fg('green_1'))}''')

  # Show the type of the value.
  opening_name = colored_stylize("type:", colored_bg("dark_cyan"))
  closing_name = colored_stylize(":type", colored_bg("dark_cyan"))
  try: print(f'  {opening_name}\n{type(value)}\n  {closing_name}')
  except: pass

  # Show the number of elements of the value, if possible.
  opening_name = colored_stylize("len:", colored_bg("dark_cyan"))
  closing_name = colored_stylize(":len", colored_bg("dark_cyan"))
  try: print(f'  {opening_name}\n{len(value)}\n  {closing_name}')
  except: pass

  # Show the type of the first element inside of the iterable value, if possible.
  opening_name = colored_stylize("type[0]:", colored_bg("dark_cyan"))
  closing_name = colored_stylize(":type[0]", colored_bg("dark_cyan"))
  try: print(f'  {opening_name}\n{type(value[0])}\n  {closing_name}')
  except: pass

  # Show the class methods of the value.
  opening_name = colored_stylize("dir:", colored_bg("dark_cyan"))
  closing_name = colored_stylize(":dir", colored_bg("dark_cyan"))
  try: print(f'  {opening_name}\n{dir(value)}\n  {closing_name}')
  except: pass

  # Show the class attributes of the value.
  opening_name = colored_stylize("dict:", colored_bg("dark_cyan"))
  closing_name = colored_stylize(":dict", colored_bg("dark_cyan"))
  try: print(f'  {opening_name}\n{value.__dict__}\n  {closing_name}')
  except: pass

  # Show the value itself.
  opening_name = colored_stylize("value:", colored_bg("dark_cyan"))
  closing_name = colored_stylize(":value", colored_bg("dark_cyan"))
  try: print(f'  {opening_name}\n{value}\n  {closing_name}')
  except: pass

  # Show the given expression of the value.
  if '__file__' in frame.f_back.f_globals:
    filename = frame.f_back.f_globals['__file__']
    relative_path = os.path.relpath(filename, os.getcwd())
    print(f'''{colored_stylize(f'from line {relative_path}:{line_number}: {expression}', colored_fg('green_1'))}''')

# PYTHON HACK: Convert a dict object into a an object where the dict keys are attributes
# See: https://stackoverflow.com/questions/59250557/how-to-convert-a-python-dict-to-a-class-object
# =====================================================================
class ObjectFromDict:
  def __init__(self, dictionary):
    for key, value in dictionary.items():
      setattr(self, key, value)
# =====================================================================

def convert_to_identifier(name):
  with_underscores = re.sub('[^a-zA-Z0-9]', '_', name)
  with_underscores = re.sub('_+', '_', with_underscores)
  with_underscores = with_underscores.strip('_')
  return with_underscores
