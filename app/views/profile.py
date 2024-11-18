def customer_base(full_name: str):
    return 'Ваш профиль:\n\n' \
        f'Имя: {full_name}'


def performer_base(full_name: str,
                   rate: float,
                   experience: int):
    return 'Ваш профиль:\n\n' \
        f'Имя: {full_name}\n' \
        f'Ставка: {rate}₽\n' \
        f'Стаж работы в годах: {experience}'


def performer_changed(full_name: str,
                      rate: float,
                      experience: int):
    return 'Информация изменена ☑️\n\n' \
        'Ваш профиль:\n\n' \
        f'Имя: {full_name}\n' \
        f'Ставка: {rate}₽\n' \
        f'Стаж работы в годах: {experience}'