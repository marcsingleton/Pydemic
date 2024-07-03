class GameOver(Exception):
    pass


class DiscardError(Exception):
    pass


class EventError(Exception):
    pass


class PropertyError(Exception):
    pass


class StationAddError(PropertyError):
    pass


class StationRemoveError(PropertyError):
    pass
