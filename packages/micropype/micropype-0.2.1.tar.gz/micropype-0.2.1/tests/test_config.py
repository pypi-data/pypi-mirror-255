import tempfile
import os.path as op

import yaml
from micropype.config import Config


@Config.register
class SubConfig(Config):
    name:   str = "Albert"
    age:    float

@Config.register
class AConfig(Config):
    num:        float = .3
    foo:        dict
    subject:    SubConfig


def test_config():
    # Create config from dict
    conf = {
        "paul": "jeje",
        "foo": {"item1": 0.1, "item2": 0.2},
        "subject": {
            "name": "ciceron",
            "age":  12
        }
    }

    config = AConfig(**conf)
    assert(config.num == .3)
    assert(config.subject.age == 12)

    # Export as yaml
    tmp_dir = tempfile.TemporaryDirectory()
    yaml_f = op.join(tmp_dir.name, "config.yaml")
    config.to_yaml(yaml_f)

    yml = yaml.safe_load(open(yaml_f, 'r'))
    assert(yml['num'] == .3)

    # Re-import from yaml
    yconfig = AConfig(yaml_f)
    assert(yconfig.foo['item2'] == config.foo['item2'])
    assert(yconfig.num == config.num)
    assert(yconfig.subject.age == config.subject.age)
    assert(yconfig.subject.name == config.subject.name)
