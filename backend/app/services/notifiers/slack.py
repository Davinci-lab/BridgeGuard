import httpx


def send(config: dict, payload: dict) -> bool:
    webhook_url = config.get("webhook_url")
    if not webhook_url:
        raise ValueError("Slack config requires webhook_url")

    text = payload.get("message", "BridgeGuard alert")
    response = httpx.post(webhook_url, json={"text": text, "payload": payload}, timeout=10)
    response.raise_for_status()
    return True
