import ipyvuetify as v


class BaseView(v.Content):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def render(self):
        pass
