from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.textinput import TextInput
from typing import List, Any


class PlayerInputRow(BoxLayout):
    """Строка ввода игрока в стартовом окне."""

    def __init__(self, index: int, remove_callback: Any, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=10, **kwargs)
        self.input = TextInput(
            hint_text=f"Игрок {index}",
            multiline=False,
            background_color=(1, 1, 1, 0.5)
        )
        self.remove_btn = Button(
            text="X",
            size_hint_x=None,
            width=dp(40),
            background_normal='',
            background_color=(0.8, 0.3, 0.3, 1)
        )
        self.remove_btn.bind(on_release=lambda x: remove_callback(self))
        self.add_widget(self.input)
        self.add_widget(self.remove_btn)


class StartupPopup(Popup):
    players_quant = 0

    def __init__(self, start_callback: Any, **kwargs):
        super().__init__(title="Знакомство с игроками", size_hint=(0.8, 0.8), auto_dismiss=False, **kwargs)
        self.start_callback = start_callback

        self.main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Контейнер для полей игроков
        self.players_container = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.players_container.bind(minimum_height=self.players_container.setter('height'))

        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.players_container)

        # Кнопка добавления (без фона)
        self.add_player_btn = Button(
            text="Добавить игрока",
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.2, 0.5, 0.8, 1),
            size_hint_y=None, height=dp(40)
        )
        self.add_player_btn.bind(on_release=self.add_player_field)

        # Кнопка Начать
        self.start_btn = Button(text="Начать", size_hint_y=None, height=dp(50), disabled=True)
        self.start_btn.bind(on_release=self.on_start)

        self.main_layout.add_widget(self.scroll)
        self.main_layout.add_widget(self.add_player_btn)
        self.main_layout.add_widget(self.start_btn)
        self.content = self.main_layout

        # Начальные 2 игрока
        self.add_player_field()
        self.add_player_field()

    def add_player_field(self, *args) -> None:
        self.players_quant += 1
        count: int = len(self.players_container.children)
        if count < 8:
            # Индекс для плейсхолдера
            idx: int = count + 1
            row = PlayerInputRow(idx, self.remove_player_field)
            row.input.bind(text=self.check_validity)
            self.players_container.add_widget(row)
            self.check_validity()

    def remove_player_field(self, row: PlayerInputRow) -> None:
        print(str(self.players_quant))
        if self.players_quant > 2:
            self.players_quant -= 1
            self.players_container.remove_widget(row)
            self.check_validity()

    def check_validity(self, *args) -> None:
        """Проверка заполнения всех полей."""
        all_filled: bool = True
        if not self.players_container.children:
            all_filled = False
        for row in self.players_container.children:
            if not row.input.text.strip():
                all_filled = False
                break
        self.start_btn.disabled = not all_filled

    def on_start(self, *args) -> None:
        names: List[str] = [row.input.text.strip() for row in reversed(self.players_container.children)]
        self.start_callback(names)
        self.dismiss()
