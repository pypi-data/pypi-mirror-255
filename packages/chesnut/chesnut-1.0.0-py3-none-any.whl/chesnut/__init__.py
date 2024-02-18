# pylint: disable=empty-docstring
import os
from .node import Node

# pdoc home page - set the __doc__ attribute to the content of the README.md file
_readme_path = os.path.join(os.path.dirname(__file__), '..', 'README.md')
with open(_readme_path, 'r', encoding='utf-8') as readme_file:
    readme_lines = readme_file.readlines()
# exclude the title, logo and any blank lines at the start of the README
for i, line in enumerate(readme_lines):
    if '<span class="pdoc-start">' in line:
        readme_lines = readme_lines[i:]
        break
__doc__ = ''.join(readme_lines)
