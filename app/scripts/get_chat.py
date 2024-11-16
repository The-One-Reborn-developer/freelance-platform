import os


def get_chat(bid_id: int,
             customer_telegram_id: int,
             performer_telegram_id: int) -> str:
    folder_path = os.path.join(os.getcwd(), "app", "chats", str(bid_id))

    file_name = f"{customer_telegram_id}_{performer_telegram_id}.txt"
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "r", encoding="utf-8") as file:
        chat = file.read()

    return chat