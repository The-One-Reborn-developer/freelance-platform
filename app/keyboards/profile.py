from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def customer_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            InlineKeyboardButton(
                text='Назад в меню 🔙',
                callback_data='menu'
            )
        ]
    )


def performer_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Изменить информацию ℹ️',
                    callback_data='change_info'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Назад в меню 🔙',
                    callback_data='menu'
                )
            ]
        ]
    )