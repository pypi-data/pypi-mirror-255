"""
Allow definition of Choices enum outside of Django.
"""
from __future__ import annotations
import enum
from types import DynamicClassAttribute
from typing import TypeVar, overload

try:
    from django.db.models.enums import ChoicesMeta, Choices, IntegerChoices, TextChoices

except ImportError:

    class ChoicesMeta(enum.EnumMeta):
        """A metaclass for creating a enum choices."""

        def __new__(metacls, classname, bases, classdict, **kwds):
            labels = []
            for key in classdict._member_names:
                value = classdict[key]
                if (
                    isinstance(value, (list, tuple))
                    and len(value) > 1
                    and isinstance(value[-1], (str, )) # NOTE: do not check for Promise (Django would be imported)
                ):
                    *value, label = value
                    value = tuple(value)
                else:
                    label = key.replace("_", " ").title()
                labels.append(label)
                # Use dict.__setitem__() to suppress defenses against double
                # assignment in enum's classdict.
                dict.__setitem__(classdict, key, value)
            cls = super().__new__(metacls, classname, bases, classdict, **kwds)
            for member, label in zip(cls.__members__.values(), labels):
                member._label_ = label
            return enum.unique(cls)

        def __contains__(cls, member):
            if not isinstance(member, enum.Enum):
                # Allow non-enums to match against member values.
                return any(x.value == member for x in cls)
            return super().__contains__(member)

        @property
        def names(cls):
            empty = ["__empty__"] if hasattr(cls, "__empty__") else []
            return empty + [member.name for member in cls]

        @property
        def choices(cls):
            empty = [(None, cls.__empty__)] if hasattr(cls, "__empty__") else []
            return empty + [(member.value, member.label) for member in cls]

        @property
        def labels(cls):
            return [label for _, label in cls.choices]

        @property
        def values(cls):
            return [value for value, _ in cls.choices]


    class Choices(enum.Enum, metaclass=ChoicesMeta):
        """Class for creating enumerated choices."""

        @DynamicClassAttribute
        def label(self):
            return self._label_

        @property
        def do_not_call_in_templates(self):
            return True

        def __str__(self):
            """
            Use value when cast to str, so that Choices set as model instance
            attributes are rendered as expected in templates and similar contexts.
            """
            return str(self.value)

        # A similar format was proposed for Python 3.10.
        def __repr__(self):
            return f"{self.__class__.__qualname__}.{self._name_}"


    class IntegerChoices(int, Choices):
        """Class for creating enumerated integer choices."""

        pass


    class TextChoices(str, Choices):
        """Class for creating enumerated string choices."""

        def _generate_next_value_(name, start, count, last_values):
            return name


T_Choices = TypeVar('T_Choices', bound=Choices)

@overload
def choices_table(arg: type[T_Choices], app_label: str = None) -> type[T_Choices]:
    ...

def choices_table(cls: type[Choices] = None, app_label: str = None):
    """
    A decorator to indicate that a table should be created for the given choices enum.
    """
    def register(cls: type[Choices]):
        if not app_label:
            raise NotImplementedError() # TODO
        
        if app_label in _registered_choices_tables:
            per_app_label = _registered_choices_tables[app_label]
        else:
            per_app_label = []
            _registered_choices_tables[app_label] = per_app_label

        per_app_label.append(cls)
    
    if cls is not None: # decorator used without arguments
        register(cls)
        return cls
    
    else: # decorator used with arguments
        def decorator(cls):
            register(cls)
            return cls

        return decorator
    
_registered_choices_tables: dict[str,list[Choices]] = {}
