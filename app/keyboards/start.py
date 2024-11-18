from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Заказчик 🤵‍♂️',
                    callback_data='customer'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Мастер 👷',
                    callback_data='performer'
                )
            ]
        ]
    )