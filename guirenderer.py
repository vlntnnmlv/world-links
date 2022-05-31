import pygame as pg
import pygame_gui as pgg

class GUIRenderer:
    
    # region Construction

    def __init__(self, surface: pg.Surface, countries: list[str]):
        self.surface = surface
        self.size = self.w, self.h = self.surface.get_size()

        self.countries = countries

        self.manager = pgg.UIManager(self.size, theme_path='theme.json')
        self.clock = pg.time.Clock()
        self.time_delta = self.clock.tick(60) / 1000.0

        self.country_buttons = dict()
        button_width = self.w / (len(self.countries) + 1) - 1
        button_height = self.h
        self.country_buttons = dict()

        self.country_buttons["full"] = pgg.elements.UIButton(
                    relative_rect=pg.Rect((0, 0), (button_width, button_height)),
                    text="full",
                    manager=self.manager)

        for i, country in enumerate(self.countries):
            self.country_buttons[country] = \
                pgg.elements.UIButton(
                    relative_rect=pg.Rect(((i + 1) * button_width, 0), (button_width, button_height)),
                    text=country,
                    manager=self.manager)

    # endregion

    # region PublicMethods

    def check_event(self, event: pg.event) -> str:
        result = None
        if event.type == pgg.UI_BUTTON_PRESSED:
                    for country, button in self.country_buttons.items():
                        if event.ui_element == button:
                            result = country
        self.manager.process_events(event)
        return result

    def render(self) -> None:
        self.manager.update(self.time_delta)
        self.manager.draw_ui(self.surface)
        self.time_delta = self.clock.tick(60) / 1000.0

    # endregion