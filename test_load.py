import pytest


@pytest.mark.parametrize(
    "yaml_raw,",
    [
        # map
        """\
line 2: two
line 1: one
line 4: four
line 3: three
""",
        # list
        """\
- line 2
- line 1
- line 4
- line 3
""",
    ],
)
def test_load_ok(prepare_yaml, helpers, yaml_raw):
    obj = prepare_yaml.load(yaml_raw)
    assert helpers.yaml_to_str(prepare_yaml, obj) == yaml_raw


@pytest.mark.xfail
@pytest.mark.parametrize(
    "yaml_raw,",
    [
        # Failed! nested seq values
        """\
- # comment
  line 1
- line 2
""",
        # Failed! nested seq values
        """\
СКЗИ Янтарь: #
  service-map-id: 287

А3: # рус.
  aliases:
  - A3 # англ.
  panda-id: 6321
""",
    ],
)
def test_load_failed(prepare_yaml, helpers, yaml_raw):
    obj = prepare_yaml.load(yaml_raw)
    assert helpers.yaml_to_str(prepare_yaml, obj) == yaml_raw
