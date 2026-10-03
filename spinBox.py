from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty
from kivy.core.window import Window

from diceWidget import DiceWidget


class CustomCounter(BoxLayout):
    value = NumericProperty(3)
    min_value = 1
    max_value = 5
    dice_value = 1

    def __init__(self, dice_value, **kwargs):
        super().__init__(**kwargs)

        self.dice_value = dice_value

        # Настройки главного контейнера
        self.orientation = 'horizontal'
        self.padding = 20
        self.spacing = 30
        self.size_hint_y = None
        self.height = 180

        self.dice_hint = DiceWidget(
            value=self.dice_value,
            click=False
        )
        self.dice_hint.bind(size=self._update_text_size)
        self.add_widget(self.dice_hint)

        # --- 2. КОНТЕЙНЕР СЧЕТЧИКА (VERTICAL) ---
        counter_box = BoxLayout(orientation='horizontal', size_hint_y=0.6)

        # Поле ввода (TextInput)
        self.input_field = TextInput(
            text=str(self.value),
            multiline=False,
            input_filter='int',
            font_size='50sp',
            halign='center',
            background_normal='',
            background_color=(0, 0, 0, 0),
            foreground_color=(0.4, 0.4, 0.4, 1)
        )
        self.input_field.bind(focus=self.on_input_focus)

        buttons_box = BoxLayout(orientation='vertical', spacing=2, size_hint_y=None, width=70)

        self.btn_plus = Button(
            text="+",
            font_size='40sp',
            background_normal='',
            background_color=(1, 0.65, 0, 1)  # Оранжевый
        )
        self.btn_plus.bind(on_release=lambda x: self.increment())

        self.btn_minus = Button(
            text="-",
            font_size='40sp',
            background_normal='',
            background_color=(1, 0.65, 0, 1)  # Оранжевый
        )
        self.btn_minus.bind(on_release=lambda x: self.decrement())

        buttons_box.add_widget(self.btn_plus)
        buttons_box.add_widget(self.btn_minus)
        
        counter_box.add_widget(self.input_field)
        counter_box.add_widget(buttons_box)

        self.add_widget(counter_box)

        # Отслеживание изменения value для обновления текста
        self.bind(value=self._update_input_text)

    def _update_text_size(self, instance, value):
        instance.text_size = instance.size

    def _update_input_text(self, instance, val):
        self.input_field.text = str(val)

    def increment(self):
        if self.value < self.max_value:
            self.value += 1

    def decrement(self):
        if self.value > self.min_value:
            self.value -= 1

    def on_input_focus(self, instance, focused):
        # Когда пользователь закончил ввод (убрал фокус)
        if not focused:
            try:
                val = int(instance.text)
                # Проверка границ
                if val < self.min_value:
                    val = self.min_value
                elif val > self.max_value:
                    val = self.max_value

                self.value = val
                instance.text = str(val)
            except ValueError:
                instance.text = str(self.value)


class MyApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        root = BoxLayout(padding=100)
        root.add_widget(CustomCounter(6))
        return root


if __name__ == '__main__':
    MyApp().run()