import os


def save_customer_chat_message(bid_id: int,
                      customer_telegram_id: int,
                      performer_telegram_id: int,
                      customer_full_name: str,
                      performer_full_name: str,
                      message: str,
                      video_file_id: str | None) -> None:
    folder_path = os.path.join(os.getcwd(), "app", "chats", str(bid_id))
    os.makedirs(folder_path, exist_ok=True)

    file_name = f"{customer_telegram_id}_{performer_telegram_id}.txt"
    file_path = os.path.join(folder_path, file_name)

    separator = "\n---\n"
    formatted_message = f"Сообщение от заказчика {customer_full_name} подрядчику {performer_full_name}:\n\n{message}\n{video_file_id}{separator}"

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(formatted_message)