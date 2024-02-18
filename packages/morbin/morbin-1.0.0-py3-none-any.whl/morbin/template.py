from morbin import Morbin, Output


class Name(Morbin):
    @property
    def program(self) -> str:
        return "name"
