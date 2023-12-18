import sys

import ruamel.yaml
from comments_sort import map_sort_before, seq_sort_before, sorted_index

yaml = ruamel.yaml.YAML()

yaml_str = """\
# comment 3.1
line 3: three  # comment 3.2
line 2:
  # comment
  line 2.2: two-two
line 1: one
 # last comment
"""

obj = yaml.load(yaml_str)
sorted_keys = sorted(
    list(obj.keys()),
    key=lambda x: x,
)
obj_sorted = map_sort_before(obj, sorted_keys)
yaml.dump(obj_sorted, sys.stdout)
print()

yaml_str = """\
  # comment 2.1
- line 2 # comment 2.2
# comment 1
- line 1
- line 4   # comment 4
- line 3
# last comment
"""

obj = yaml.load(yaml_str)
obj_sorted = seq_sort_before(obj, sorted_index(obj))
yaml.dump(obj_sorted, sys.stdout)
print()
