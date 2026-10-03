import typing
from diceWidget import *
from startScreen import StartupPopup
from spinBox import CustomCounter
from winWidget import VictoryPopup

import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import NumericProperty
from typing import List, Union, Any, Dict
from enum import Enum



# Настройка окна (желтоватый фон по умолчанию)
Window.clearcolor = (0.99, 0.98, 0.92, 1)
placeholders: List[str] = [f"1", f"2", f"3", f"4", f"5", f"6", f"Итог",
                                    f"Пара", f"2 пары", f"Сет", f"Малый стрит",
                                    f"Большой стрит", f"Четные", f"Нечетные",
                                    f"Фулл-хаус", f"Каре", f"Покер", f"Итог"]



class Cell:
    """Класс-обертка для ячейки таблицы."""

    def __init__(self, widget: Union[Button, Label, TextInput]):
        self.widget: Union[Button, Label, TextInput] = widget
        self.value: str = ""



class PaperWidget(BoxLayout):
    """Базовый класс со стилизацией под бумагу."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            # Цвет бумажного листа (чуть желтоватый)
            Color(0.9, 0.98, 0.92, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance: Any, value: Any) -> None:
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class StyledButton(Button):
    """Кнопка, стилизованная под надпись ручкой на бумаге."""

    p_idx = NumericProperty(0)
    r_idx = NumericProperty(0)

    def __init__(self, tp:str = "School", **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_disabled_normal = ''
        self.background_color = (0, 0, 0, 0)  # Прозрачный фон
        self.color = (0.1, 0.1, 0.6, 1)  # Цвет синей ручки
        self.font_size = '16sp'
        self.type = tp   # "School"||"Choose and Co eff"||"Factual"
        self.activated = False

        with self.canvas.before:
            # Слой для затемнения неактивного столбца
            self.overlay_color = Color(0, 0, 0, 0)
            self.overlay_rect = Rectangle(size=self.size, pos=self.pos)

        with self.canvas.after:
            Color(0.6, 0.6, 0.6, 1)  # Цвет карандашной линии
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, *args) -> None:
            self.line.rectangle = (self.x, self.y, self.width, self.height)
            self.overlay_rect.pos = self.pos
            self.overlay_rect.size = self.size

    def on_disabled(self, instance, value):
        """Автоматически срабатывает при изменении self.disabled."""
        if value:
            self.overlay_color.rgba = (0, 0, 0, 0.15)  # Затемняем (15% черного)
        else:
            self.overlay_color.rgba = (0, 0, 0, 0)


class TableCellWidget(Label):
    """Виджет текста, стилизованный под карандашную ячейку."""

    def __init__(self, is_header: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.color = (0, 0, 0, 1) if not is_header else (0.2, 0.2, 0.2, 1)
        self.bold = is_header
        with self.canvas.after:
            Color(0.7, 0.7, 0.7, 1)
            self.line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self._update_line, size=self._update_line)

    def _update_line(self, *args) -> None:
        self.line.rectangle = (self.x, self.y, self.width, self.height)


class MainScreen(BoxLayout):
    activ_cell = 0
    content = None
    players = []

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.player_columns: List[List[StyledButton]] = []
        self.current_player_index = 0

        # 1. Поле для кнопок меню
        self.menu_area = PaperWidget(size_hint_y=None, height=dp(50))

        self.add_widget(self.menu_area)

        # Контейнер для таблицы со скроллом
        self.scroll = ScrollView(do_scroll_x=True, do_scroll_y=True)

        self.grid = GridLayout(rows=len(placeholders)+1, orientation='tb-lr', size_hint=(None, None), spacing=0)
        self.grid.bind(minimum_width=self.grid.setter('width'), minimum_height=self.grid.setter('height'))

        self.scroll.add_widget(self.grid)
        self.add_widget(self.scroll)

    def count_range(self, range_start, range_finish):
        res = 0
        for i in range(range_start, range_finish):
            cell = self.player_columns[self.current_player_index-1][i]
            print(cell.text)
            if cell.text == "":
                res *= -1
                break

            elif cell.text == "-":
                 res += 0

            else:
                res += int(cell.text)

        return res

    def count_school(self, args):
        # Проходим по строкам с 1 по 6
        sum_res: int = self.count_range(0, 6)

        if sum_res > 0:
            if sum_res > 63:
                sum_res += 35
            print("2 = ", sum_res)
            self.player_columns[self.current_player_index-1][6].text = str(sum_res)

    def build_table(self, player_names: List[str]) -> None:
        self.grid.clear_widgets()
        self.player_columns = []
        self.current_player_index = 0

        self.players = player_names

        self.grid.add_widget(TableCellWidget(text="", is_header=True, size_hint=(None, None), size=(dp(120), dp(40))))
        # Сами названия категорий
        for ph in placeholders:
            self.grid.add_widget(TableCellWidget(text=ph, is_header=True, size_hint=(None, None), size=(dp(120), dp(40))))

        # --- ПОСЛЕДУЮЩИЕ КОЛОНКИ: Игроки ---
        for p_idx, name in enumerate(player_names):
            column_buttons = []
            # 1. Заголовок колонки (Имя игрока)
            header = TableCellWidget(text=name, is_header=True, size_hint=(None, None), size=(dp(120), dp(40)))
            self.grid.add_widget(header)

            # 2. Ячейки для записи очков в этой колонке
            for r_idx, ph in enumerate(placeholders):
                btn = StyledButton(text="", size_hint=(None, None), size=(dp(120), dp(40)))
                btn.p_idx = p_idx
                btn.r_idx = r_idx
                btn.category_name = ph
                btn.player_name = name

                if r_idx in [6, 17]:
                    btn.disabled = True
                else:
                    btn.bind(on_release=self.open_cell_popup)
                self.grid.add_widget(btn)

                column_buttons.append(btn)


            self.player_columns.append(column_buttons)
        self.update_active_player()

    def update_active_player(self):
        """Метод для включения/выключения кнопок в зависимости от текущего хода."""
        for idx, column in enumerate(self.player_columns):
            is_active = (idx == self.current_player_index)
            for btn in column:
                # Кнопка активна только если сейчас ход этого игрока И в ней еще нет текста
                if btn.text == "":
                    btn.disabled = not is_active
                else:
                    btn.disabled = True  # Заполненные ячейки всегда неактивны

    def next_turn(self):
        """Переход хода к следующему игроку."""
        self.current_player_index = ((self.current_player_index + 1) % len(self.player_columns))
        self.update_active_player()

    def final_score(self):
        fin_scores = []
        for i in self.player_columns:
            fin_scores.append(int(i[17].text))

        max_score = max(fin_scores)
        all_win_indices = [i for i, value in enumerate(fin_scores) if value == max_score]
        winners = ""
        if len(all_win_indices) == 1:
            winners = self.players[all_win_indices[0]]
        else:
            for s in all_win_indices:
                winners += self.players[all_win_indices[s]] + ", "
            winners = winners[:-2]

        popup = VictoryPopup(winner=winners, score=str(max_score))
        popup.open()

    def check_num_even(self, instance, value):
        if not value:
            return

        if value.startswith('-'):
            instance.text = value[1:]
            return

        if value.isdigit():
            answer = int(value)

            if answer > 36:
                answer = 36
                instance.text = "36"

            elif answer == 0 and value == '0':
                answer = 2
                instance.text = "2"

            if answer % 2 != 0:
                self.content.children[0].children[0].disabled = True
            else:
                self.content.children[0].children[0].disabled = False

    def check_num_odd(self, instance, value):
        if not value:
            return

        if value.startswith('-'):
            instance.text = value[1:]
            return

        if value.isdigit():
            answer = int(value)

            if answer > 36:
                answer = 35
                instance.text = "35"

            elif answer == 0 and value == '0':
                answer = 1
                instance.text = "1"

            if answer % 2 != 0:
                self.content.children[0].children[0].disabled = False
            else:
                self.content.children[0].children[0].disabled = True

    def count_all(self, args):
        sum_res: int = self.count_range(6, 17)

        if sum_res > 0:
            res = sum_res
            while res > 100:
                sum_res += 50
                res -= 100

            self.player_columns[self.current_player_index-1][17].text = str(sum_res)
            if self.player_columns[self.current_player_index][17].text:
                self.final_score()

    def open_cell_popup(self, instance: StyledButton) -> None:
        self.content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.activ_cell = instance.r_idx + 1
        lbl = Label(
            text="Выберите выпавшие значения",
            size_hint_y=0.2,
            color=(0, 0, 0, 1)  # Черный текст
        )
        grid = None

        match self.activ_cell:
            case 8 | 9 | 10 | 16:
                # 2. Сетка кубиков
                dice_app_instance = DiceApp()
                grid = dice_app_instance.build() if self.activ_cell != 9 else dice_app_instance.build(dcs=2)
                grid.size_hint_y = 0.6
            case 1 | 2 | 3 | 4 | 5 | 6:
                grid = CustomCounter(self.activ_cell)
            case 11 | 12 | 15 | 17:
                hand_type = ""
                result = 0
                match self.activ_cell:
                    case 11:
                        hand_type = "Малый стрит"
                        result = 25
                    case 12:
                        hand_type = "Большой стрит"
                        result = 35
                    case 15:
                        hand_type = "Фулл-хаус"
                        result = 40
                    case 17:
                        hand_type = "Покер"
                        result = 50
                lbl.size_hint_y = 0.8
                lbl.text = f"{hand_type} приносит {int(result)} очков"
                grid = Label(text="", height=dp(1))

            case 13 | 14:
                lbl.text = "Введите сумарное значение на кубах"
                grid = TextInput(
                    hint_text=f"Поле для ввода суммы",
                    multiline=False,
                    background_color=(1, 1, 1, 0.5),
                    size_hint_y=0.6,
                    input_filter='int'
                )
                if self.activ_cell == 13:
                    grid.bind(text=self.check_num_even)
                else:
                    grid.bind(text=self.check_num_odd)
                #Написать функцию check_num для общего вызова окна, а even и odd закинуть в подтверждение проверки

            case _:
                print("Автопропуск")

        self.content.add_widget(lbl)
        self.content.add_widget(grid)
        # 3. Кнопка: size_hint_y=0.2 (20% высоты)
        btn_confirm = Button(
            text="Подтвердить",
            size_hint_x=0.4
        )
        btn_pass = Button(
            text="Пропустить",
            size_hint_x=0.4
        )
        btn_container = BoxLayout(
            orientation="horizontal",
            spacing=dp(20),
            size_hint_y=0.2
        )
        btn_container.add_widget(btn_pass)
        btn_container.add_widget(btn_confirm)

        self.content.add_widget(btn_container)

        # Создаем Popup
        popup = Popup(title="Результат броска", content=self.content, size_hint=(None, None), size=(dp(300), dp(400)), auto_dismiss=False)

        def confirm(obj: Any) -> None:
            result: int = 0
            check_sch: int = 0

            match self.activ_cell:
                case 9:
                    check = True
                    for i in grid.children:
                        if i.selected:
                            check = not check
                            result += i.value
                    if check:
                        result *= 2
                    else:
                        result *= 4

                case 8 | 10 | 16:
                    dice_quant = 0
                    match self.activ_cell:
                        case 8:
                            dice_quant = 2
                        case 10:
                            dice_quant = 3
                        case 16:
                            dice_quant = 4
                        case _:
                            print("Автопропуск")
                    for i in grid.children:
                        if i.selected:
                            result = i.value
                            break
                    result *= dice_quant

                case 1 | 2 | 3 | 4 | 5 | 6:
                    result = grid.value * self.activ_cell
                    check_sch += 1
                    popup.bind(on_dismiss=self.count_school)

                case 11:
                    result = 25
                case 12:
                    result = 35
                case 15:
                    result = 40
                case 17:
                    result = 50

                case 13 | 14:
                    if grid.text == "":
                        result = 0
                    else:
                        result = int(grid.text)
                    

                case _:
                    print("Автопропуск")

            popup.bind(on_dismiss=self.count_all)
            instance.text = str(result)
            instance.activated = True
            popup.dismiss()

        def pass_roll(obj: Any) -> None:
            instance.text = '-'
            instance.activated = True
            if self.activ_cell in [1, 2, 3, 4, 5, 6]:
                popup.bind(on_dismiss=self.count_school)
            popup.bind(on_dismiss=self.count_all)
            popup.dismiss()

        btn_pass.bind(on_release=pass_roll)
        btn_confirm.bind(on_release=confirm)
        popup.open()
        self.next_turn()


class TableApp(App):
    def build(self) -> MainScreen:
        self.main_screen = MainScreen()
        return self.main_screen

    def on_start(self) -> None:
        # Показываем всплывающее окно при запуске
        popup = StartupPopup(start_callback=self.setup_table)
        popup.open()

    def setup_table(self, player_names: List[str]) -> None:
        self.main_screen.build_table(player_names)


if __name__ == '__main__':
    TableApp().run()