"""Objects maintaining global shared state."""


class GameState:
    def __init__(
        self,
        cities,
        disease_track,
        players,
        player_order,
        player_deck,
        infection_deck,
        outbreak_track,
        infection_track,
        station_count,
        turn_count,
        draw_count,
        infect_count,
    ):
        self.cities = cities
        self.disease_track = disease_track
        self.players = players
        self.player_order = player_order
        self.player_deck = player_deck
        self.infection_deck = infection_deck
        self.outbreak_track = outbreak_track
        self.infection_track = infection_track
        self.station_count = station_count
        self.turn_count = turn_count
        self.draw_count = draw_count
        self.infect_count = infect_count

    @property
    def current_player(self):
        turn = self.turn_count % len(self.players)
        return self.players[self.player_order[turn]]
