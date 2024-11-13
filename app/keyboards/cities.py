from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def cities_keyboard() -> InlineKeyboardMarkup:
    with open('app/temp/cities.txt', 'r', encoding='utf-8') as f:
        cities = f.read().split('\n')

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
                    text='Назад в меню 🔙',
                    callback_data='menu'
                )
            ]
        ]
    )