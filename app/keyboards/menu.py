from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def customer_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Опубликовать новый заказ 🏷️',
                    callback_data='new_bid'
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
            ]
        ]
    )