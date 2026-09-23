"""Envoi de messages vers Telegram via l'API Bot HTTP (aucune lib tierce Telegram nécessaire)."""

import requests

TELEGRAM_MAX_LEN = 4000  # marge sous la limite réelle de 4096 caractères


def _split_message(text: str, max_len: int = TELEGRAM_MAX_LEN):
    """Découpe le texte en morceaux < max_len, de préférence sur des sauts de paragraphe."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    remaining = text
    while len(remaining) > max_len:
        cut = remaining.rfind("\n\n", 0, max_len)
        if cut == -1:
            cut = remaining.rfind("\n", 0, max_len)
        if cut == -1:
            cut = max_len
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks


def send_telegram_report(bot_token: str, chat_id: str, title: str, text: str):
    """Envoie le rapport complet sous forme d'une série de messages Telegram."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    chunks = _split_message(text)
    total = len(chunks)

    for i, chunk in enumerate(chunks, start=1):
        header = f"{title}" if i == 1 else f"{title} (suite {i}/{total})"
        payload = f"{header}\n\n{chunk}"
        resp = requests.post(url, data={"chat_id": chat_id, "text": payload}, timeout=30)
        resp.raise_for_status()


def send_telegram_document(bot_token: str, chat_id: str, file_path: str, caption: str = ""):
    """Envoie aussi le rapport en pièce jointe (archive complète, utile si tu veux le relire)."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, "rb") as f:
        resp = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption[:1024]},
            files={"document": f},
            timeout=60,
        )
    resp.raise_for_status()
