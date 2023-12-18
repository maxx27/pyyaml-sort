
<!-- https://gist.github.com/maxx27/81c148d76dd1c025ce43ca1835c152af -->

# PyYAML

[PyYAML](https://pypi.org/project/PyYAML/) doesn't support comments:

```python
import sys
import yaml

yaml_str = """\
# comment 1
line 1: one # comment 2
# comment 3
"""

obj = yaml.load(yaml_str, Loader=yaml.FullLoader)
yaml.dump(obj, sys.stdout)
```

Output is:

```yaml
line 1: one
```

# ruamel.yaml

[ruamel.yaml](https://pypi.org/project/ruamel.yaml/) supports comments:

```python
import sys
import ruamel.yaml

yaml_str = """\
# comment 1
line 1: one # comment 2
# comment 3
"""

yaml = ruamel.yaml.YAML()
obj = yaml.load(yaml_str)
yaml.dump(obj, sys.stdout)
```

Output is:

```yaml
# comment 1
line 1: one # comment 2
# comment 3
```

## Sorting YAML with comments

Comments are not [documented well](https://yaml.readthedocs.io/en/latest/detail/#round-trip-including-comments) (unfortunately).
So many information was acquired from [StackOverflow user Anthon](https://stackoverflow.com/users/1307905/anthon):

- https://stackoverflow.com/questions/52043027/get-comment-during-iteration-in-ruamel-yaml
- https://stackoverflow.com/questions/56166055/how-can-i-add-a-comment-with-ruamel-yaml
- https://stackoverflow.com/questions/72732098/keeping-comments-in-ruamel-yaml
- https://stackoverflow.com/questions/36969808/can-i-insert-a-line-into-ruamel-yamls-commentedmap
- https://stackoverflow.com/questions/76975731/end-of-line-comments-and-before-after-key-comments-made-using-ruamel-yaml-are-no
- https://stackoverflow.com/questions/47382227/python-yaml-update-preserving-order-and-comments
- https://stackoverflow.com/questions/56471040/add-a-comment-in-list-element-in-ruamel-yaml

(if you don't have `ruamel.yaml` installed you can find sources for comments [here](https://gemfury.com/aroundthecode/python:ruamel.yaml/-/content/yaml/comments.py))

But I found [this question](https://stackoverflow.com/questions/49613901/sort-yaml-file-with-comments) without answer and I need this too. So this gist is my answer.

Main point about comments that _in_ `ruamel.yaml` they refer to the current line or line above:

```yaml
- one # comment to the current line
# comment to the line above
- two
```

But [many people consider](https://softwareengineering.stackexchange.com/questions/126601/comment-before-or-after-the-relevant-code/126603#126603) them in different way:

```yaml
- one # comment to the current line
# comment to the line below
- two
```

Sorting this way requires more efforts.

### Sorting dict and list

Use function `map_sort_before` to sort maps:

```python
import sys

import ruamel.yaml
from comments_sort import map_sort_before

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
```

Output is:

```yaml
line 1: one
line 2:
  # comment
  line 2.2: two-two
# comment 3.1
line 3: three  # comment 3.2
 # last comment
```

Use function `seq_sort_before` and `sorted_index` to sort sequences:

```python
import sys

import ruamel.yaml
from comments_sort import seq_sort_before, sorted_index

yaml = ruamel.yaml.YAML()
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
```

Output is:

```yaml
# comment 1
- line 1
  # comment 2.1
- line 2 # comment 2.2
- line 3
- line 4   # comment 4
# last comment
```

`sorted_index` is a helper function that returns new indices to construct new sequence. See the description of the function for more details.

## Some critics for the implementation

You must provide sort information in advance (as argument for the functions) because you construct new YAML object while sorting. I tried an implementation with sorting parameters (to call `sorted` inside the functions) but I don't like how it looks.

Pairs of functions are very similar:

- `_get_map_comments` and `_get_seq_comments`
- `map_sort_before` and `seq_sort_before`

It could be implemented using [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).
