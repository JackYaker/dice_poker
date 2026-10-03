from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder

Builder.load_string("""
<VictoryPopup>:
    title: "Победа!"
    title_align: "center"
    size_hint: (0.6, 0.45)
    auto_dismiss: False          # запрет закрытия по клику вне окна
    separator_color: 1, 0.84, 0, 1

    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15

        # ── Победитель ──
        Label:
            text: f"Победитель: [b]{root.winner_name}[/b]"
            markup: True
            font_size: "22sp"
            color: 1, 0.84, 0, 1

        # ── Очки ──
        Label:
            text: f"Общее количество очков: {root.total_score}"
            font_size: "18sp"
            color: 0.85, 0.85, 0.85, 1

        # ── Кнопка ──
        Button:
            text: "Завершить"
            font_size: "20sp"
            size_hint_y: 0.35
            background_color: 0.2, 0.6, 0.86, 1
            on_release: root.dismiss()
""")

class VictoryPopup(Popup):
    """Всплывающее окно с результатами игры."""

    winner_name = StringProperty("Игрок 1")
    total_score = StringProperty("0")

    def __init__(self, winner: str = "Игрок 1", score: str = "0", **kwargs):
        super().__init__(**kwargs)
        self.winner_name = winner
        self.total_score = score
