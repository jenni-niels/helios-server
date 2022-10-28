# We want to generate ballots with different numbers of questions

# We want to test ballots with 1-10 questions
num_questions = [1, 2, 5, 10]
num_choices_per_question = [2, 4, 5, 10]

ballot = []
for c in num_choices_per_question:
    ballot = []
    for q in num_questions:
        question = {"answer_urls":[None for None in range(c)]
                    "answers": [str(answer) for answer in range(c)],
                    "choice_type": "approval",
                    "max": c,
                    "min": 0,
                    "question": f"Choose your favorite numbers [0-{str(c)})",
                    "result_type": "absolute",
                    "short_name": "choose",
                    "tally_type": "homomorphic",
                   }
        ballot.append(question)

