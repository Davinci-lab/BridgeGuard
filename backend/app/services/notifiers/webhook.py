import httpx


def send(config: dict, payload: dict) -> bool:
    url = config.get("url")
    if not url:
        raise ValueError("Webhook config requires url")

    headers = config.get("headers") or {}
    response = httpx.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    return True
