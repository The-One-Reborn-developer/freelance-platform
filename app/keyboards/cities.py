from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def cities_keyboard() -> InlineKeyboardMarkup:
    with open('app/temp/cities.txt', 'r', encoding='utf-8') as f:
        cities = f.read().splitlines()

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=city,
                    callback_data=city
                )
            ] for city in cities
        ]
        + [
            [
                InlineKeyboardButton(
                    text='Назад 🔙',
                    callback_data='menu'
                )
            ]
        ]
    )