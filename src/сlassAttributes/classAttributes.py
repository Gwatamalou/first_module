from datetime import datetime, timezone


class ClassMeta(type):
    def __new__(cls, name, base, attrs):
        attrs.update(created_at=datetime.now(timezone.utc))
        return super().__new__(cls, name, base, attrs)


class DateClass(metaclass=ClassMeta):
    @classmethod
    def get_created_at(cls):
        return cls.created_at


print(DateClass.get_created_at())
