from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def start_kb():
    kb_list = [[KeyboardButton(text="▶️ Начать диалог")],
               [KeyboardButton(text="▶️ Выбрать режим диалога")]]
    
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Чтоб начать диалог с ботом жмите 👇:"
    )


def stop_speak():
    kb_list = [[KeyboardButton(text="❌ Завершить диалог")]]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Чтоб завершить диалог с ботом жмите 👇:"
    )

def select_dialog_mode():
    inline_kb_list = [
        [InlineKeyboardButton(text="Помошник-программист", callback_data='get_help_developer')],
        [InlineKeyboardButton(text="ИТ-документация", callback_data='it_docs')],
        [InlineKeyboardButton(text="1C документация", callback_data='it_one_c')],
        [InlineKeyboardButton(text="Общая информация", callback_data='all_docs')],
        [InlineKeyboardButton(text="Без всего общалка", callback_data='balabolka')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    