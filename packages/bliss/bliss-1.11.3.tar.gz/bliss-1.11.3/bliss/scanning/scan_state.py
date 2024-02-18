import enum


class ScanStateMeta(enum.EnumMeta):
    def __call__(cls, value, *args, **kw):
        if isinstance(value, str):
            try:
                value = cls.__members__[value].value
            except KeyError:
                raise ValueError(f"'{value}' is not a valid ScanState") from None
        return super().__call__(value, *args, **kw)


class ScanState(enum.IntEnum, metaclass=ScanStateMeta):
    IDLE = 0
    PREPARING = 1
    STARTING = 2
    STOPPING = 3
    DONE = 4
    USER_ABORTED = 5
    KILLED = 6

    def __str__(self):
        return self.name

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, str):
            return self.name == __value
        return super().__eq__(__value)

    def __hash__(self) -> int:
        return super().__hash__()
