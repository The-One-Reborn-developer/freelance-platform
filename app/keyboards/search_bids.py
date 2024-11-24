from aiogram.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup)


def respond_or_look_keyboard(bid) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Откликнуться 🖐️',
                                        callback_data=str(bid['id']))
            ],
            [
                InlineKeyboardButton(text='Посмотреть переписки заказчика 📨',
                                        callback_data=f'look_customer_chats_{bid["customer_telegram_id"]}')
            ]
        ]
    )


def look_bid_chat_keyboard(bid_id: int,
                           customer_telegram_id: int,
                           performer_telegram_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Смотреть переписку этого заказа 📨',
                                        callback_data=f'look_customer_chat_{bid_id}_{customer_telegram_id}_{performer_telegram_id}')
            ]
        ]
    )