from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup)


def chat_answer_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Ответить ✉️',
                    callback_data=f'answer_{telegram_id}'
                )
            ]
        ]
    )