from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def instrument_provided_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Да ✔️',
                    callback_data='yes'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Нет ❌',
                    callback_data='no'
                )
            ]
        ]
    )