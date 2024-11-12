from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def customer_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Опубликовать новый заказ 🏷️',
                    callback_data='new_bid'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Просмотреть мои заказы 📂',
                    callback_data='look_bids'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Сменить информацию профиля 👤',
                    callback_data='profile'
                )
            ]
        ]
    )


def performer_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Искать заказы 🔎',
                    callback_data='search_bids'
                )
            ],
            [
                InlineKeyboardButton(
                    text='Сменить информацию профиля 👤',
                    callback_data='profile'
                )
            ]
        ]
    )