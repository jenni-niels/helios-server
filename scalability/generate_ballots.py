import json
import os

def generate_ballot(num_q, num_c):
    question = {"answer_urls":[None for _ in range(num_c)],
                    "answers": [str(answer) for answer in range(num_c)],
                    "choice_type": "approval",
                    "max": num_c,
                    "min": 0,
                    "question": f"Choose your favorite numbers [0-{str(num_c)})",
                    "result_type": "absolute",
                    "short_name": "choose",
                    "tally_type": "homomorphic",
                   }
    ballot = num_q * [question]
    return ballot

os.makedirs("ballots", exist_ok=True)

# We want to test ballots with 1-10 questions
num_questions = [1, 2, 5, 10]
# and 2-10 choices per question
num_choices_per_question = [2, 4, 5, 10]

for num_q in num_questions:
    for num_c in num_choices_per_question:
        ballot = generate_ballot(num_q, num_c)
        json.dump(ballot, open(f"ballots/{num_q}Q_{num_c}C.json", "w"))
