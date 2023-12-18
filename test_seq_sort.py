import pytest


@pytest.mark.parametrize(
    "yaml_raw, yaml_sorted",
    [
        (
            # no comments
            """\
- line 2
- line 1
- line 4
- line 3
""",
            """\
- line 1
- line 2
- line 3
- line 4
""",
        ),
        (
            # line 2
            """\
- line 2 # 2.1
- line 1
- line 4
- line 3
""",
            """\
- line 1
- line 2 # 2.1
- line 3
- line 4
""",
        ),
        (
            # line 1
            """\
- line 2
- line 1 # 1.1
- line 4
- line 3
""",
            """\
- line 1 # 1.1
- line 2
- line 3
- line 4
""",
        ),
        (
            # line 3
            """\
- line 2
- line 1
- line 4
- line 3 # 3.1
""",
            """\
- line 1
- line 2
- line 3 # 3.1
- line 4
""",
        ),
        (
            # line 4
            """\
- line 2
- line 1
- line 4 # 4.1
- line 3
""",
            """\
- line 1
- line 2
- line 3
- line 4 # 4.1
""",
        ),
        (
            # two spaces before "inline" comment
            """\
- line 2
- line 1
- line 4  # 4.1
- line 3
""",
            """\
- line 1
- line 2
- line 3
- line 4  # 4.1
""",
        ),
        (
            # two spaces before "before" comment
            """\
- line 2
- line 1
  # 4.1
- line 4
- line 3
""",
            """\
- line 1
- line 2
- line 3
  # 4.1
- line 4
""",
        ),
        (
            # two spaces before "last" comment
            """\
- line 2
- line 1
- line 4
- line 3
  # last
""",
            """\
- line 1
- line 2
- line 3
- line 4
  # last
""",
        ),
        (
            # multiple lines "last" comment
            """\
- line 2
- line 1
- line 4
- line 3
# last 1
  # last 2
# last 3
""",
            """\
- line 1
- line 2
- line 3
- line 4
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
- line 3 # 3.3
# 1.1
# 1.2
- line 1
# 2.1
# 2.2
- line 2 # 2.3
- line 5
- line 4
# last
""",
            """\
# 1.1
# 1.2
- line 1
# 2.1
# 2.2
- line 2 # 2.3
# 3.1 comment to line 3
# 3.2 three three
- line 3 # 3.3
- line 4
- line 5
# last
""",
        ),
    ],
)
def test_seq_sort(prepare_yaml, helpers, yaml_raw, yaml_sorted):
    assert helpers.sort_seq_and_str(prepare_yaml, yaml_raw) == yaml_sorted
