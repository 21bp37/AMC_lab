"""
Moduł: pipeline/gemini_batch_labeler.py (Wersja Lokalna - Ollama)
Wykorzystuje model uruchomiony lokalnie na Twojej karcie graficznej.
Brak limitów zapytań, przerw i ukrytych kosztów.
"""

import json
import pandas as pd
from pathlib import Path
from openai import OpenAI

# Połączenie z lokalnym serwerem Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Klucz jest wymagany przez bibliotekę, ale Ollama go ignoruje
)

MODEL_NAME = "qwen2.5:3b"
INPUT_CSV = Path("ukraine-source/twitter_unique_llm.csv")
PROMPT_FILE = Path("prompts/gemini_codebook.txt")

# Mniejsza paczka dla stabilności mniejszego modelu (lepsze trzymanie formatu JSON)
BATCH_SIZE = 10

def clean_json_response(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

if not INPUT_CSV.exists() or not PROMPT_FILE.exists():
    raise FileNotFoundError("Brak pliku z danymi lub promptu!")

df = pd.read_csv(INPUT_CSV, low_memory=False)

if "llm_label" not in df.columns:
    df["llm_label"] = ""
else:
    df["llm_label"] = df["llm_label"].astype(object).fillna("").astype(str)

unlabeled_mask = (df["llm_label"] == "") | (df["llm_label"].str.strip() == "") | (df["llm_label"] == "nan")
unlabeled_indices = df[unlabeled_mask].index.tolist()

already_labeled_count = len(df) - len(unlabeled_indices)

print(f" Status pliku: {len(df):,} wszystkich wierszy.")
print(f" Już zaetykietowano: {already_labeled_count:,}")
print(f" Pozostało: {len(unlabeled_indices):,}")
print(f" Aktywny model (Lokalny): {MODEL_NAME}")

if len(unlabeled_indices) == 0:
    print(" Wszystkie wpisy zostały już zaetykietowane!")
    exit(0)

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    system_prompt = f.read()

print("\n Rozpoczynanie etykietowania lokalnego (maksymalna prędkość GPU)...")

for i in range(0, len(unlabeled_indices), BATCH_SIZE):
    batch_idx = unlabeled_indices[i:i + BATCH_SIZE]
    batch_df = df.loc[batch_idx]

    payload = []
    for idx, row in batch_df.iterrows():
        payload.append({
            "id": int(row["unique_id"]),
            "text": str(row["Tweet"])[:400]
        })

    user_message = f"Przeanalizuj poniższą paczkę wpisów. Zwróć WYŁĄCZNIE tablicę JSON:\n{json.dumps(payload, ensure_ascii=False)}"

    success = False
    retries = 0

    while not success and retries < 3:
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.0
            )

            raw_text = response.choices[0].message.content
            cleaned_text = clean_json_response(raw_text)
            parsed = json.loads(cleaned_text)

            for item in parsed:
                raw_uid = item.get("id")
                label = item.get("label", "")

                if raw_uid is not None and label:
                    try:
                        uid = int(raw_uid)
                        df.loc[df["unique_id"] == uid, "llm_label"] = str(label)
                    except ValueError:
                        pass

            success = True
            current_progress = i + len(batch_idx)
            pct = (current_progress / len(unlabeled_indices)) * 100
            print(f" Postęp: {current_progress:,} / {len(unlabeled_indices):,} wpisów ({pct:.1f}%)")

        except Exception as e:
            print(f" Błąd parsowania JSON (próba {retries + 1}/3). Model wygenerował nieprawidłowy format. Ponawiam...")
            retries += 1

    try:
        df.to_csv(INPUT_CSV, index=False, encoding="utf-8-sig")
    except PermissionError:
        print(" OSTRZEŻENIE: Zamknij plik CSV w Excelu!")

print("\n Zakończono etykietowanie!")