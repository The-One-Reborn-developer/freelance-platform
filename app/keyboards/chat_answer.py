from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup)


def chat_answer_keyboard(bid_id: int,
                         customer_telegram_id: int,
                         performer_telegram_id: int,
                         is_customer: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Ответить ✉️',
                    callback_data=f'answer_{bid_id}_{customer_telegram_id}_{performer_telegram_id}_{is_customer}'
                )
            ]
        ]
    )