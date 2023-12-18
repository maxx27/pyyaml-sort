import pytest


@pytest.mark.parametrize(
    "yaml_raw, yaml_sorted",
    [
        (
            # no comments
            """\
line 2: two
line 1: one
line 4: four
line 3: three
""",
            """\
line 1: one
line 2: two
line 3: three
line 4: four
""",
        ),
        (
            # line 2
            """\
line 2: two # 2.1
line 1: one
line 4: four
line 3: three
""",
            """\
line 1: one
line 2: two # 2.1
line 3: three
line 4: four
""",
        ),
        (
            # line 1
            """\
line 2: two
line 1: one # 1.1
line 4: four
line 3: three
""",
            """\
line 1: one # 1.1
line 2: two
line 3: three
line 4: four
""",
        ),
        (
            # line 3
            """\
line 2: two
line 1: one
line 4: four
line 3: three # 3.1
""",
            """\
line 1: one
line 2: two
line 3: three # 3.1
line 4: four
""",
        ),
        (
            # line 4
            """\
line 2: two
line 1: one
line 4: four # 4.1
line 3: three
""",
            """\
line 1: one
line 2: two
line 3: three
line 4: four # 4.1
""",
        ),
        (
            # two spaces before "inline" comment
            """\
line 2: two
line 1: one
line 4: four  # 4.1
line 3: three
""",
            """\
line 1: one
line 2: two
line 3: three
line 4: four  # 4.1
""",
        ),
        (
            # two spaces before "before" comment
            """\
line 2: two
line 1: one
  # 4.1
line 4: four
line 3: three
""",
            """\
line 1: one
line 2: two
line 3: three
  # 4.1
line 4: four
""",
        ),
        (
            # two spaces before "last" comment
            """\
line 2: two
line 1: one
line 4: four
line 3: three
  # last
""",
            """\
line 1: one
line 2: two
line 3: three
line 4: four
  # last
""",
        ),
        (
            # multiple lines "last" comment
            """\
line 2: two
line 1: one
line 4: four
line 3: three
# last 1
  # last 2
# last 3
""",
            """\
line 1: one
line 2: two
line 3: three
line 4: four
# last 1
  # last 2
# last 3
""",
        ),
        (
            # complex case
            """\
# 3.1 comment to line 3
# 3.2 three three
line 3: three # 3.3
# 1.1
# 1.2
line 1: one
# 2.1
# 2.2
line 2: two # 2.3
line 5: five
line 4: four
# last
""",
            """\
# 1.1
# 1.2
line 1: one
# 2.1
# 2.2
line 2: two # 2.3
# 3.1 comment to line 3
# 3.2 three three
line 3: three # 3.3
line 4: four
line 5: five
# last
""",
        ),
        (
            # nested values
            """\
line 3: three
line 2:
  line 2.2: two-two
line 1: one
""",
            """\
line 1: one
line 2:
  line 2.2: two-two
line 3: three
""",
        ),
        (
            # nested values with "inline" comments
            """\
line 3: three
line 2: # comment
  line 2.2: two-two
line 1: one
""",
            """\
line 1: one
line 2: # comment
  line 2.2: two-two
line 3: three
""",
        ),
        (
            # nested values with "start" comments
            """\
line 3: three
line 2:
  # comment
  line 2.2: two-two
line 1: one
""",
            """\
line 1: one
line 2:
  # comment
  line 2.2: two-two
line 3: three
""",
        ),
        (
            # nested values with "start" comments
            """\
# comment
line 2:
  line 2.2: two-two
line 3: three
""",
            """\
# comment
line 2:
  line 2.2: two-two
line 3: three
""",
        ),
        (
            # nested seq values
            """\
a:
- line 1
- line 2
""",
            """\
a:
- line 1
- line 2
""",
        ),
    ],
)
def test_map_sort(prepare_yaml, helpers, yaml_raw, yaml_sorted):
    assert helpers.sort_map_and_str(prepare_yaml, yaml_raw) == yaml_sorted
