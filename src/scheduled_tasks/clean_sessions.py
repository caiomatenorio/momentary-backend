from ..app import app
from ..libs.scheduler import scheduler
from ..services import session_service


@scheduler.task("cron", id="clean_sessions", hour="*", minute=0)
def clean_expired_sessions():
    with app.app_context():
        print("Cleaning expired sessions...")
        session_service.clean_expired_sessions()
