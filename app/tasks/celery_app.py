import celery
import logging


app = celery.Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

app.conf.update(
    task_routes={
        'app.tasks.celery_app.*': {'queue': 'all_queues'}
    },
    broker_connection_retry_on_startup=True
)


@app.task
def create_tables_task():
    logging.info('Creating tables...')
    
    from app.database.queries.create_tables import create_tables

    result = create_tables()
    if result:
        logging.info('Tables created successfully')
    else:
        logging.error('Error creating tables')


@app.task
def close_bid_task(bid_id: int):
    logging.info(f'Closing bid {bid_id}...')
    
    from app.database.queries.close_bid import close_bid
    
    result = close_bid(bid_id)
    if result:
        logging.info(f'Bid {bid_id} closed successfully')
    else:
        logging.error(f'Error closing bid {bid_id}')


@app.task
def get_all_customer_chats_task(customer_telegram_id: int) -> list | None:
    logging.info(f'Getting all customer chats for {customer_telegram_id}...')
    
    from app.database.queries.get_all_customer_chats import get_all_customer_chats
    
    result = get_all_customer_chats(customer_telegram_id)
    if result != [] and result is not None:
        logging.info(f'All customer chats for {customer_telegram_id} retrieved successfully')
        return result
    elif result == []:
        logging.info(f'No customer chats found for {customer_telegram_id}')
        return []
    else:
        logging.error(f'Error getting all customer chats for {customer_telegram_id}')
        return None
    

@app.task
def get_all_performer_chats_task(performer_telegram_id: int) -> list | None:
    logging.info(f'Getting all performer chats for {performer_telegram_id}...')
    
    from app.database.queries.get_all_performer_chats import get_all_performer_chats
    
    result = get_all_performer_chats(performer_telegram_id)
    if result != [] and result is not None:
        logging.info(f'All performer chats for {performer_telegram_id} retrieved successfully')
        return result
    elif result == []:
        logging.info(f'No performer chats found for {performer_telegram_id}')
        return []
    else:
        logging.error(f'Error getting all performer chats for {performer_telegram_id}')
        return None
    

@app.task
def get_bid_by_bid_id_task(bid_id: int) -> list | None:
    logging.info(f'Getting bid {bid_id}...')
    
    from app.database.queries.get_bid_by_bid_id import get_bid_by_bid_id
    
    result = get_bid_by_bid_id(bid_id)
    if result != [] and result is not None:
        logging.info(f'Bid {bid_id} retrieved successfully')
        return result
    elif result == []:
        logging.info(f'No bid found for {bid_id}')
        return []
    else:
        logging.error(f'Error getting bid {bid_id}')
        return None
    

@app.task
def get_bids_by_city_task(city: str) -> list[dict] | None:
    logging.info(f'Getting bids by city {city}...')
    
    from app.database.queries.get_bids_by_city import get_bids_by_city
    
    result = get_bids_by_city(city)
    if result != [] and result is not None:
        logging.info(f'Bids by city {city} retrieved successfully')
        return result
    elif result == []:
        logging.info(f'No bids by city {city}')
        return []
    else:
        logging.error(f'Error getting bids by city {city}')
        return None
    

@app.task
def get_bids_by_telegram_id_task(telegram_id: int) -> list[dict] | None:
    logging.info(f'Getting bids by telegram id {telegram_id}...')
    
    from app.database.queries.get_bids_by_telegram_id import get_bids_by_telegram_id
    
    result = get_bids_by_telegram_id(telegram_id)
    if result != [] and result is not None:
        logging.info(f'Bids by telegram id {telegram_id} retrieved successfully')
        return result
    elif result == []:
        logging.info(f'No bids by telegram id {telegram_id}')
        return []
    else:
        logging.error(f'Error getting bids by telegram id {telegram_id}')
        return None
    

@app.task
def get_responses_by_bid_id_task(bid_id: int) -> list[dict] | None:
    logging.info(f'Getting responses by bid id {bid_id}...')
    
    from app.database.queries.get_responses_by_bid_id import get_responses_by_bid_id
    
    result = get_responses_by_bid_id(bid_id)
    if result != [] and result is not None:
        logging.info(f'Responses by bid id {bid_id} retrieved successfully')
        return result
    elif result == []:
        logging.info(f'No responses by bid id {bid_id}')
        return []
    else:
        logging.error(f'Error getting responses by bid id {bid_id}')
        return None
    

@app.task
def get_responses_by_performer_telegram_id_task(performer_telegram_id: int) -> list[dict] | None:
    logging.info(f'Getting responses by performer telegram id {performer_telegram_id}...')
    
    from app.database.queries.get_responses_by_performer_telegram_id import get_responses_by_performer_telegram_id
    
    result = get_responses_by_performer_telegram_id(performer_telegram_id)
    if result != [] and result is not None:
        logging.info(f'Responses by performer telegram id {performer_telegram_id} retrieved successfully')
        return result
    elif result == []:
        logging.info(f'No responses by performer telegram id {performer_telegram_id}')
        return []
    else:
        logging.error(f'Error getting responses by performer telegram id {performer_telegram_id}')
        return None
    

@app.task
def get_user_by_telegram_id_task(telegram_id: int) -> list | None:
    logging.info(f'Getting user by telegram id {telegram_id}...')
    
    from app.database.queries.get_user_by_telegram_id import get_user_by_telegram_id
    
    result = get_user_by_telegram_id(telegram_id)
    if result != [] and result is not None:
        logging.info(f'User by telegram id {telegram_id} retrieved successfully')
        return result
    elif result == []:
        logging.info(f'No user by telegram id {telegram_id}')
        return []
    else:
        logging.error(f'Error getting user by telegram id {telegram_id}')
        return None
    

@app.task
def post_bid_task(customer_telegram_id: int,
                  city: str,
                  description: str,
                  deadline: str,
                  instrument_provided: bool) -> bool | None:
    logging.info(f'Posting bid for {customer_telegram_id}...')
    
    from app.database.queries.post_bid import post_bid
    
    result = post_bid(customer_telegram_id, city, description, deadline, instrument_provided)
    if result == True:
        logging.info(f'Bid for {customer_telegram_id} posted successfully')
        return True
    elif result == False:
        logging.info(f'Bid for {customer_telegram_id} already exists')
        return False
    else:
        logging.error(f'Error posting bid for {customer_telegram_id}')
        return None
    

@app.task
def post_response_task(bid_id: int,
                       performer_telegram_id: int,
                       performer_full_name: str,
                       performer_rate: float,
                       performer_experience: int) -> bool | None:
    logging.info(f'Posting response for {bid_id} from {performer_telegram_id}...')
    
    from app.database.queries.post_response import post_response
    
    result = post_response(bid_id, performer_telegram_id, performer_full_name, performer_rate, performer_experience)
    if result == True:
        logging.info(f'Response for {bid_id} from {performer_telegram_id} posted successfully')
        return True
    elif result == False:
        logging.info(f'Response for {bid_id} from {performer_telegram_id} already exists')
        return False
    else:
        logging.error(f'Error posting response for {bid_id} from {performer_telegram_id}')
        return None
    

@app.task
def post_user_task(telegram_id: int) -> None:
    logging.info(f'Posting user {telegram_id}...')
    
    from app.database.queries.post_user import post_user
    
    post_user(telegram_id)

    logging.info(f'User {telegram_id} posted successfully')


@app.task
def put_response_task(bid_id: int, performer_telegram_id: int, **kwargs) -> None:
    logging.info(f'Updating response for {bid_id} from {performer_telegram_id}...')
    
    from app.database.queries.put_response import put_response
    
    put_response(bid_id, performer_telegram_id, **kwargs)

    logging.info(f'Response for {bid_id} from {performer_telegram_id} updated successfully')


@app.task
def put_user_task(telegram_id: int, **kwargs) -> None:
    logging.info(f'Updating user {telegram_id}...')
    
    from app.database.queries.put_user import put_user
    
    put_user(telegram_id, **kwargs)

    logging.info(f'User {telegram_id} updated successfully')


if __name__ == '__main__':
    app.start()