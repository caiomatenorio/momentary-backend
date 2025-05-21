from src.service import session_service
from src.singleton.app import app
from src.singleton.scheduler import scheduler


@scheduler.task("cron", id="clean_sessions", hour="*/1")
def clean_expired_sessions():
    with app.app_context():
        print("Cleaning expired sessions...")
        session_service.clean_expired_sessions()
