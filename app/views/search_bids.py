def bid_info(bid,
             customer_full_name) -> str:
    return f'<b>Номер заказа:</b> <u>{bid["id"]}</u>\n' \
        f'<b>Заказчик:</b> <i>{customer_full_name}</i>\n' \
        f'<b>Описание:</b> {bid["description"]}\n' \
        f'<b>Сроки выполнения работы:</b> <i>{bid["deadline"]}</i>\n' \
        f'<b>Предоставляет инструмент:</b> <i>{"Да" if bid["instrument_provided"] == 1 else "Нет"}</i>'


def no_available_bids() -> str:
    return 'На данный момент нет свободных заказов 🙁'


def look_customer_chats_base_content(bid_id: int,
                                     bid_data: list) -> str:
    return f'<b>Номер заказа:</b> <u>{bid_id}</u>\n' \
        f'<b>Город:</b> <i>{bid_data[2]}</i>\n' \
        f'<b>Описание:</b> {bid_data[3]}\n' \
        f'<b>Сроки выполнения работы:</b> <i>{bid_data[4]}</i>\n' \
        f'<b>Предоставляет инструмент:</b> <i>{"Да" if bid_data[5] == 1 else "Нет"}</i>\n' \
        f'<b>Статус:</b> <i>{"Выполнен" if bid_data[6] == 1 else "Не выполнен"}</i>\n\n'


def look_customer_chats_additional_content(response) -> str:
    return f'<b>Откликнулся:</b> <i>{response["performer_full_name"]}</i>\n' \
        f'<b>Ставка:</b> <i>{response["performer_rate"]}</i>\n' \
        f'<b>Стаж:</b> <i>{response["performer_experience"]}</i>'


def look_customer_chats_no_responses(bid_id: int,
                                     bid_data: list) -> str:
    return f'<b>Номер заказа:</b> <u>{bid_id}</u>\n' \
        f'<b>Город:</b> <i>{bid_data[2]}</i>\n' \
        f'<b>Описание:</b> {bid_data[3]}\n' \
        f'<b>Сроки выполнения работы:</b> <i>{bid_data[4]}</i>\n' \
        f'<b>Предоставляет инструмент:</b> <i>{"Да" if bid_data[5] == 1 else "Нет"}</i>\n' \
        f'<b>Статус:</b> <i>{"Выполнен" if bid_data[6] == 1 else "Не выполнен"}</i>\n\n' \
        'На данный заказ ещё нет откликов 🙁'


def customer_no_chats() -> str:
    return 'У данного заказчика ещё нет переписок.'


def already_responded() -> str:
    return 'Вы уже откликнулись на данный заказ!'


def successfully_responded(bid_id) -> str:
    return f'Вы успешно откликнулись на заказ №{bid_id}!\n' \
        'Заказчик получит уведомление о Вашем отклике.'


def click_again() -> str:
    return 'Нажмите ещё раз "Ответить", чтобы войти в переписку.'