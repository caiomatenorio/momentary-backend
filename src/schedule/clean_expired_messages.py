from src.service import chat_service
from src.singleton.app import app
from src.singleton.scheduler import scheduler


@scheduler.task("cron", id="clean_expired_messages", minute="*/1")
def clean_expired_messages():
    with app.app_context():
        print("Cleaning expired messages...")
        chat_service.clean_expired_messages()
