# Veille automatique — Cybersécurité & Autodidacte

Deux rapports quotidiens envoyés sur Telegram, générés avec l'API Gemini (gratuite, avec recherche web activée). Le backend LLM est interchangeable — passage prévu vers Perplexity plus tard (voir `llm_backend.py`).

## 1. Récupérer une clé Gemini (gratuite)

1. Va sur https://aistudio.google.com/apikey
2. Connecte-toi avec un compte Google
3. Clique "Create API key" → copie la clé (tu ne la reverras qu'une fois en entier)
4. Aucune carte bancaire requise pour le tier gratuit

Limites du tier gratuit (largement suffisant pour 2 rapports/jour) : Gemini 2.5 Flash → 10 requêtes/min, 250/jour.

## 2. Créer le bot Telegram

1. Ouvre Telegram, cherche **@BotFather**
2. Envoie `/newbot`, suis les instructions (nom + username se terminant par "bot")
3. BotFather te donne un **token** (garde-le secret)
4. Démarre une conversation avec ton nouveau bot (cherche son username, clique "Démarrer")
5. Récupère ton **chat_id** :
   - Envoie n'importe quel message à ton bot
   - Va sur `https://api.telegram.org/bot<TON_TOKEN>/getUpdates` dans un navigateur
   - Cherche `"chat":{"id": ...}` dans la réponse JSON → c'est ton chat_id

## 3. Configuration

```bash
cd veille
cp .env.example .env
```

Remplis `.env` avec ta clé Gemini, le token du bot, et ton chat_id.

```bash
pip install -r requirements.txt
```

## 4. Tester manuellement

```bash
python veille.py cyber
python veille.py autodidacte
```

Tu dois recevoir les messages (et le fichier en pièce jointe) sur Telegram en 30 secondes à 2 minutes selon la longueur du rapport.

## 5. Programmer l'envoi automatique (cron)

```bash
crontab -e
```

Ajoute (adapte le chemin vers le dossier `veille` et vers ton python) :

```cron
0 6 * * * cd /chemin/vers/veille && /usr/bin/python3 veille.py cyber >> reports/cron.log 2>&1
30 6 * * * cd /chemin/vers/veille && /usr/bin/python3 veille.py autodidacte >> reports/cron.log 2>&1
```

→ Rapport cyber à 6h00, rapport autodidacte à 6h30, tous les jours.

**Important** : cron ne tourne que si la machine est allumée à l'heure prévue. Si tu veux que ça tourne même PC éteint, il faudra héberger ce dossier sur un petit VPS (quelques euros/mois) plus tard — le code ne change pas, seul l'endroit où il tourne change.

## 6. Basculer vers Perplexity plus tard

Dans `.env` :
```
LLM_BACKEND=perplexity
PERPLEXITY_API_KEY=ta_cle
```
Vérifie juste le nom de modèle "sonar" en cours sur https://docs.perplexity.ai avant de basculer (peut changer avec le temps). Rien d'autre à modifier.

## Ajuster le contenu des rapports

Les prompts sont dans `prompts/veille_cybersecurite.md` et `prompts/veille_autodidacte.md` — éditables en texte libre, pas besoin de toucher au code Python pour changer les sections ou l'angle du rapport.

## 7. Alternative gratuite pour tourner même PC éteint — GitHub Actions

Le cron local (partie 7 plus haut) ne marche que si ton ordinateur est allumé à l'heure prévue. **GitHub Actions** fait tourner le script sur les serveurs de GitHub à ta place, gratuitement, sans carte bancaire, même PC éteint. Le fichier `.github/workflows/veille.yml` fourni est déjà prêt pour ça.

### Pourquoi ce choix plutôt qu'un autre
- 100 % gratuit, aucune carte bancaire requise
- Aucune limite pratique : le job tourne ~2 minutes x 2 fois/jour, largement sous le quota gratuit (2000 min/mois sur dépôt privé, illimité sur dépôt public)
- Chaque rapport généré est automatiquement re-commité dans le dépôt (dossier `reports/`) → ça te fait un historique consultable ET ça garde le dépôt "actif" (GitHub désactive les tâches planifiées après 60 jours sans activité — le commit automatique règle ce problème tout seul)

*Autres options qui existent : PythonAnywhere (interface simple, mais tâches planifiées limitées sur le compte gratuit) et Google Cloud Scheduler (généreux mais demande de lier une carte bancaire même si rien n'est facturé). GitHub Actions reste le plus simple à zéro contrainte.*

### Mise en place

1. Va sur https://github.com, crée un compte si tu n'en as pas (gratuit)
2. Clique le **+** en haut à droite → **New repository**
3. Donne-lui un nom, ex. `veille-perso` → coche **Private** → **Create repository**
4. Sur la page du nouveau dépôt, clique **uploading an existing file** (ou "Add file" → "Upload files")
5. Glisse-dépose **tout le contenu** du dossier `veille/` (y compris le dossier `.github` et `prompts`, mais **PAS** le fichier `.env` — il ne doit jamais aller sur GitHub) → **Commit changes**
6. Va dans **Settings** (onglet en haut du dépôt) → **Actions** → **General** → descends jusqu'à "Workflow permissions" → sélectionne **Read and write permissions** → **Save** (nécessaire pour que le job puisse commiter les rapports)
7. Toujours dans **Settings** → **Secrets and variables** → **Actions** → **New repository secret**, crée ces 3 secrets un par un (nom exact à gauche, valeur à droite) :
   - `GEMINI_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
8. Va dans l'onglet **Actions** du dépôt → clique le workflow **Veille quotidienne** dans la liste à gauche → bouton **Run workflow** (à droite) → **Run workflow** pour tester manuellement tout de suite, sans attendre 6h
9. Après ~1-2 minutes, vérifie Telegram (le rapport doit arriver) et l'onglet Actions (coche verte = succès, croix rouge = erreur, clique dessus pour voir le détail du log)

Une fois testé, les deux jobs tourneront automatiquement chaque matin à 6h00 et 6h30, heure d'Abidjan (le fuseau d'Abidjan est UTC, donc pas de conversion à faire). Les horaires peuvent être retardés de quelques minutes en cas de forte charge sur GitHub — normal, pas un bug.
