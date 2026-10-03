import typing
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty, BooleanProperty
from kivy.graphics import InstructionGroup, Color, RoundedRectangle, Ellipse, Line


class DiceWidget(ButtonBehavior, Widget):
    selected = BooleanProperty(False)
    value = NumericProperty(1)
    padding = dp(4)
    L, C, R = 0.22, 0.5, 0.78
    patterns = {
        1: [(C, C)],
        2: [(L, L), (R, R)],
        3: [(L, L), (C, C), (R, R)],
        4: [(L, L), (L, R), (R, L), (R, R)],
        5: [(L, L), (L, R), (C, C), (R, L), (R, R)],
        6: [(L, L), (L, C), (L, R), (R, L), (R, C), (R, R)]
    }

    def __init__(self, value, dcs=1, click=True, **kwargs):
        super().__init__(**kwargs)
        self.value = value

        self.body_group = InstructionGroup()
        self.dots_group = InstructionGroup()
        self.selection_group = InstructionGroup()

        self.canvas.add(self.body_group)
        self.canvas.add(self.dots_group)
        self.canvas.add(self.selection_group)

        self.bind(pos=self.update_all, size=self.update_all)
        self.bind(value=self.update_dots)
        # ВАЖНО: Привязываем обновление графики к изменению переменной selected
        if click:
            self.bind(selected=self.update_selection)


    def update_all(self, *args):
        self.update_body()
        self.update_dots(self.value)
        self.update_selection()

    def update_body(self):
        self.body_group.clear()
        # Защита от отрицательных размеров, если виджет сжат слишком сильно
        side = max(0, min(self.width, self.height) - self.padding * 2)
        x = self.x + (self.width - side) / 2
        y = self.y + (self.height - side) / 2

        # Сделал цвет чуть темнее (0.9), чтобы было видно на светлом фоне
        self.body_group.add(Color(0.9, 0.9, 0.9, 1))
        self.body_group.add(RoundedRectangle(pos=(x, y), size=(side, side), radius=[5]))

        # Добавим тонкую рамку для тела кубика, чтобы его было видно всегда
        self.body_group.add(Color(0.7, 0.7, 0.7, 1))
        self.body_group.add(Line(rounded_rectangle=(x, y, side, side, 5), width=1))

    def update_dots(self, value, *args):
        self.dots_group.clear()
        side = max(0, min(self.width, self.height) - self.padding * 2)
        x = self.x + (self.width - side) / 2
        y = self.y + (self.height - side) / 2
        dot_size = side * 0.18

        self.dots_group.add(Color(0.1, 0.1, 0.1, 1))
        for px, py in self.patterns.get(value, []):
            dot_x = x + (px * side) - (dot_size / 2)
            dot_y = y + (py * side) - (dot_size / 2)
            self.dots_group.add(Ellipse(pos=(dot_x, dot_y), size=(dot_size, dot_size)))

    def update_selection(self, *args):
        self.selection_group.clear()
        if self.selected:
            side = max(0, min(self.width, self.height) - self.padding * 2)
            x = self.x + (self.width - side) / 2
            y = self.y + (self.height - side) / 2

            self.selection_group.add(Color(0, 0.5, 1, 1))  # Синий цвет
            # width=2 делает рамку заметнее
            self.selection_group.add(Line(rounded_rectangle=(x, y, side, side, 5), width=2))


class DiceApp(App):
    choosen: int = 0
    cell_type: typing.AnyStr = ''
    active_quant: typing.List[int] = []
    now_dice = 0

    def choose(self, dice):
        if dice.selected:
            self.now_dice -= 1
            self.choosen -= dice.value
            dice.selected = False

        elif self.now_dice+1 <= self.max_dices:
            self.now_dice += 1
            self.choosen += dice.value
            dice.selected = True
        else:
            var = None

    def build(self, dcs=1, col=3, row=2, dices=6, celt=''):
        self.max_dices = dcs
        self.now_dice = 0
        self.cell_type = celt
        layout = GridLayout(cols=col, rows=row, spacing=dp(10), padding=dp(10))

        for i in range(1, dices + 1):
            dice = DiceWidget(value=i)
            dice.bind(on_press=self.choose)
            layout.add_widget(dice)

        return layout


if __name__ == '__main__':
    DiceApp().run()