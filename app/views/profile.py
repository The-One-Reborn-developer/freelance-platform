def customer_base(full_name: str) -> str:
    return 'Ваш профиль:\n\n' \
        f'Имя: {full_name}'


def performer_base(full_name: str,
                   rate: float,
                   experience: int) -> str:
    return 'Ваш профиль:\n\n' \
        f'Имя: {full_name}\n' \
        f'Ставка: {rate}₽\n' \
        f'Стаж работы в годах: {experience}'


def performer_changed(full_name: str,
                      rate: float,
                      experience: int) -> str:
    return 'Информация изменена ☑️\n\n' \
        'Ваш профиль:\n\n' \
        f'Имя: {full_name}\n' \
        f'Ставка: {rate}₽\n' \
        f'Стаж работы в годах: {experience}'