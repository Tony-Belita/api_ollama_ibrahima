import requests
import json
import time
from html import unescape


# Récupérer les questions de l'API OpenTDB
def charger_questions(amount=20):
    url = f"https://opentdb.com/api.php?amount=50&type=multiple"
    response = requests.get(url)
    data = response.json()
    questions = data.get("results", [])
    return questions


# Sauvegarder les questions dans un fichier JSON
def sauvegarder(questions, filename="questions.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)


# Interroger Llama3.2 via l’API Ollama locale
def interro_llama(prompt, model="llama3.2"):
    url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"Erreur lors de l'appel à Ollama : {e}"


# Évaluer les réponses
def evaluer_model(questions):
    correct = 0
    total = len(questions)

    for i, q in enumerate(questions, 1):
        question = unescape(q["question"])
        correct_answer = unescape(q["correct_answer"])
        all_answers = [unescape(a) for a in q["incorrect_answers"] + [correct_answer]]
        all_answers.sort()

        prompt = f"""Réponds à cette question à choix multiple en donnant uniquement la bonne réponse (texte exact) :

Question : {question}
Choix : {', '.join(all_answers)}

Reponse :"""

        print(f"\n Question {i}/{total}")
        print(f"Prompt envoyé :\n{prompt}")
        response = interro_llama()
        print(f"Réponse du modèle : {response}")
        print(f"Réponse attendue : {correct_answer}")

        if correct_answer.lower() in response.lower():
            print(" Bonne réponse")
            correct += 1
        else:
            print(" Mauvaise réponse")

        time.sleep(1.5)  # Petite pause pour éviter de spammer l'API

    success_rate = (correct / total) * 100
    print(f"\n Taux de bonnes réponses : {success_rate:.2f}%")
    return success_rate


# Étape principale
def main():
    print(" Récupération des questions...")
    questions = charger_questions(20)
    sauvegarder(questions)
    print(" Questions sauvegardées dans 'questions.json'")

    print(" Évaluation du modèle Llama3.2...")
    evaluer_model(questions)


if __name__ == "__main__":
    main()
