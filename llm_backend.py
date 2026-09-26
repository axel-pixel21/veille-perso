"""
Couche d'abstraction pour le générateur de rapport.

Aujourd'hui : Gemini (Google AI Studio), gratuit, avec recherche web activée
(grounding Google Search).

Plus tard : quand l'abonnement Perplexity sera pris, il suffira de :
  1. Compléter PERPLEXITY_API_KEY dans .env
  2. Mettre LLM_BACKEND=perplexity dans .env
  3. Vérifier sur https://docs.perplexity.ai le nom de modèle "sonar" en cours
     (l'API Perplexity est compatible OpenAI, endpoint https://api.perplexity.ai/chat/completions)
Rien d'autre ne change : veille.py appelle toujours generate_report(prompt).
"""

import os


def generate_report(prompt: str) -> str:
    backend = os.environ.get("LLM_BACKEND", "gemini").lower()
    if backend == "gemini":
        return _generate_gemini(prompt)
    elif backend == "perplexity":
        return _generate_perplexity(prompt)
    else:
        raise ValueError(f"Backend LLM inconnu : {backend}")


def _generate_gemini(prompt: str) -> str:
    from google import genai
    from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

    api_key = os.environ["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

    google_search_tool = Tool(google_search=GoogleSearch())

    # Modèle configurable via la variable GEMINI_MODEL (secret GitHub ou .env) —
    # pratique pour basculer rapidement si un modèle est à court de quota gratuit.
    model = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
    print(f"[debug] Modèle Gemini effectivement utilisé : {model}")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            temperature=0.4,
        ),
    )
    return response.text


def _generate_perplexity(prompt: str) -> str:
    import requests

    api_key = os.environ["PERPLEXITY_API_KEY"]
    # Vérifie le nom de modèle actuel dans la doc Perplexity avant de basculer
    # (au moment de l'écriture de ce script, la famille "sonar" fait de la
    # recherche web native).
    model = os.environ.get("PERPLEXITY_MODEL", "sonar-pro")

    resp = requests.post(
        "https://api.perplexity.ai/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
