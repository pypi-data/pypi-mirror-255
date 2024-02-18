from simplegmail import Gmail

from agentic.core import action, workflow, Config, require_config


GMAIL_CLIENT_SECRET_PATH = Config(
    name="GMAIL_CLIENT_SECRET_PATH", description="Client secret JSON path for Gmail"
)


@action()
async def send_email(
    to: str,
    sender: str,
    subject: str,
    msg_html: str,
    msg_plain: str = "",
    signature: bool = True,
):
    """Send an email using Gmail."""
    client_secret_path = (require_config(GMAIL_CLIENT_SECRET_PATH),)
    gmail = Gmail(client_secret_path)
    gmail.send_message(
        to=to,
        sender=sender,
        subject=subject,
        msg_html=msg_html,
        msg_plain=msg_plain,
        signature=signature,
    )
