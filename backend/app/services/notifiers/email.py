from email.message import EmailMessage
import smtplib


def send(config: dict, payload: dict) -> bool:
    host = config.get("smtp_host")
    to_address = config.get("to")
    from_address = config.get("from") or config.get("username")
    if not host or not to_address or not from_address:
        raise ValueError("Email config requires smtp_host, from, and to")

    port = int(config.get("smtp_port", 587))
    message = EmailMessage()
    message["Subject"] = config.get("subject", "BridgeGuard alert")
    message["From"] = from_address
    message["To"] = to_address
    message.set_content(payload.get("message", "BridgeGuard alert"))

    with smtplib.SMTP(host, port, timeout=10) as smtp:
        if config.get("use_tls", True):
            smtp.starttls()
        username = config.get("username")
        password = config.get("password")
        if username and password:
            smtp.login(username, password)
        smtp.send_message(message)
    return True
