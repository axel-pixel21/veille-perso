"""
Génère le briefing quotidien (cyber ou autodidacte) et l'envoie sur Telegram.

Usage :
    python veille.py cyber
    python veille.py autodidacte

À programmer avec cron pour un envoi automatique chaque matin (voir README.md).
"""

import argparse
import datetime
import os
import pathlib
import sys

from dotenv import load_dotenv

from llm_backend import generate_report
from telegram_sender import send_telegram_report, send_telegram_document

BASE_DIR = pathlib.Path(__file__).resolve().parent

TOPICS = {
    "cyber": {
        "prompt_file": BASE_DIR / "prompts" / "veille_cybersecurite.md",
        "title": "🛡️ Veille Cybersécurité & Réseaux",
    },
    "autodidacte": {
        "prompt_file": BASE_DIR / "prompts" / "veille_autodidacte.md",
        "title": "📚 Veille Autodidacte",
    },
}


def main():
    parser = argparse.ArgumentParser(description="Génère et envoie un rapport de veille quotidien.")
    parser.add_argument("topic", choices=TOPICS.keys())
    parser.add_argument(
        "--no-document",
        action="store_true",
        help="N'envoie pas le fichier en pièce jointe, seulement les messages texte.",
    )
    args = parser.parse_args()

    load_dotenv(BASE_DIR / ".env")

    cfg = TOPICS[args.topic]
    today = datetime.date.today().isoformat()

    prompt = cfg["prompt_file"].read_text(encoding="utf-8").replace("{{DATE}}", today)

    print(f"[{today}] Génération du rapport '{args.topic}'...", file=sys.stderr)
    try:
        report = generate_report(prompt)
    except Exception as exc:
        print(f"Erreur lors de la génération du rapport : {exc}", file=sys.stderr)
        sys.exit(1)

    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / f"{args.topic}_{today}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Rapport sauvegardé : {report_path}", file=sys.stderr)

    bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    title = f"{cfg['title']} — {today}"

    print("Envoi sur Telegram...", file=sys.stderr)
    send_telegram_report(bot_token, chat_id, title, report)

    if not args.no_document:
        send_telegram_document(bot_token, chat_id, str(report_path), caption=title)

    print("Terminé.", file=sys.stderr)


if __name__ == "__main__":
    main()
