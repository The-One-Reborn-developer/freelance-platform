import celery
import logging


app = celery.Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
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
    
    from app.database.queues.create_tables import create_tables

    result = create_tables()
    if result:
        logging.info('Tables created successfully')
    else:
        logging.error('Error creating tables')


@app.task
def close_bid_task(bid_id: int):
    logging.info(f'Closing bid {bid_id}...')
    
    from app.database.queues.close_bid import close_bid
    
    result = close_bid(bid_id)
    if result:
        logging.info(f'Bid {bid_id} closed successfully')
    else:
        logging.error(f'Error closing bid {bid_id}')


@app.task
def get_all_customer_chats_task(customer_telegram_id: int) -> list:
    logging.info(f'Getting all customer chats for {customer_telegram_id}...')
    
    from app.database.queues.get_all_customer_chats import get_all_customer_chats
    
    result = get_all_customer_chats(customer_telegram_id)
    if result:
        logging.info(f'All customer chats for {customer_telegram_id} retrieved successfully')

        return result
    else:
        logging.error(f'Error getting all customer chats for {customer_telegram_id}')

        return []
    

@app.task
def get_all_performer_chats_task(performer_telegram_id: int) -> list:
    logging.info(f'Getting all performer chats for {performer_telegram_id}...')
    
    from app.database.queues.get_all_performer_chats import get_all_performer_chats
    
    result = get_all_performer_chats(performer_telegram_id)
    if result:
        logging.info(f'All performer chats for {performer_telegram_id} retrieved successfully')

        return result
    else:
        logging.error(f'Error getting all performer chats for {performer_telegram_id}')

        return []
    

@app.task
def get_bid_by_id_task(bid_id: int) -> list:
    logging.info(f'Getting bid {bid_id}...')
    
    from app.database.queues.get_bid_by_id import get_bid_by_id
    
    result = get_bid_by_id(bid_id)
    if result:
        logging.info(f'Bid {bid_id} retrieved successfully')

        return result
    else:
        logging.error(f'Error getting bid {bid_id}')

        return []