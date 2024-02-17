from dataclasses import dataclass, asdict, fields


@dataclass
class InternalBaseInterface:
    def __init__(self, **kwargs):
        valid_fields = {f.name: kwargs.get(f.name) for f in fields(self)}
        for name, value in valid_fields.items():
            setattr(self, name, value)

    def to_dict(self):
        return asdict(self)
