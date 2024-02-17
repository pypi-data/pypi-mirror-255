from warnings import warn
import yaml
from micropype.utils import MessageIntent, cprint, merge_dicts


def read_annotations(cls):
    """ 
        Parameters
        ==========
    
    """
    attributes = {}
    for attr, attr_type in cls.__annotations__.items():
        default = cls.__getattribute__(cls, attr) if hasattr(cls, attr) else None
        t = attr_type.__name__
        attributes[attr] = (t, default)
    return attributes


class Config:
    _children = {}

    def __init__(self, yaml_f=None, priority="yaml", **kwargs) -> None:
        """
            Parameters
            ==========
            yaml_f: str
            priority: "yaml" or "kwargs"
                Which config values to use even if defined in the other method.
        """
        if yaml_f is not None:
            ycfg = yaml.safe_load(open(yaml_f, 'r'))
            if priority == "yaml":
                kwargs = merge_dicts(kwargs, ycfg)
            elif priority == "kwargs":
                kwargs = merge_dicts(ycfg, kwargs)
            else:
                raise ValueError("")

        attributes = read_annotations(self.__class__)

        used_kwargs = 0 
        for attr_name, (attr_t, default_v) in attributes.items():
            useDefault = not attr_name in kwargs
            if not useDefault:
                used_kwargs += 1

            if attr_t in self._children:
                value = self._children[attr_t] if useDefault else self._children[attr_t](**kwargs[attr_name])
            else:
                value = default_v if useDefault else kwargs[attr_name]
            self.__setattr__(attr_name, value)
        if used_kwargs < len(kwargs.keys()):
            for k in kwargs.keys():
                if not k in attributes.keys():
                    cprint(
                        f'"{k}" is not an attribute of {self.__class__.__name__}. Skipping this setting.',
                        intent=MessageIntent.WARNING
                    )
                    continue

    @classmethod
    def register(cls, child_class):
        cls._children[child_class.__name__] = child_class
        return child_class
    

    def to_dict(self) -> dict:
        result = {}
        for name, value in self.__dict__.items():
            if isinstance(value, Config):
                result[name] = value.to_dict()
            elif isinstance(value, list):
                result[name] = [item.to_dict() if isinstance(item, Config) else item for item in value]
            elif isinstance(value, dict):
                result[name] = {key: value.to_dict() if isinstance(value, Config) else value for key, value in value.items()}
            else:
                result[name] = value
        return result

    def to_yaml(self, filepath:str):
        with open(filepath, 'w') as fp:
            yaml.dump(self.to_dict(), fp)


# if __name__ == "__main__":
#     class SubConfig(Config):
#         name:   str = "Albert"
#         age:    float
#     class AConfig(Config):
#         num:        float = .3
#         foo:        dict
#         subject:    SubConfig

#     conf = {
#         "paul": "jeje",
#         "foo": {"item1": 0.1, "item2": 0.2},
#         "subject": {
#             "name": "ciceron",
#             "age":  12
#         }
#     }

#     config = AConfig(**conf)
#     pass
