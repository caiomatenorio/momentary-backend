from src.service import chat_service
from src.singleton.app import app
from src.singleton.scheduler import scheduler


@scheduler.task("cron", id="clean_empty_chats", hour="*/1")
def clean_empty_chats():
    with app.app_context():
        print("Cleaning empty chats...")
        chat_service.clean_empty_chats()
