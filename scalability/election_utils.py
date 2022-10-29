import sys
sys.path.append("../../helios-server/")
import helios.models as models
from helios_auth import models as auth_models
from helios.models import Voter
import random
import uuid

def election_info(election):
    print(f"Election: {election.name}")
    print(f" -- Num Trustees: {election.num_trustees}")
    print(f" -- Num Voters: {election.num_voters}")
    print(f" -- Num Votes: {election.num_cast_votes}")
    num_questions = len(election.questions)
    print(f" -- Num Questions: {num_questions}")
    print(f" -- Num Choices: {len(election.questions[0]['answers']) if num_questions > 0 else 0}")
    return

def delete_all_voters(election):
    for v in Voter.get_by_election(election):
        v.delete()
    return

def add_voters(election, num_voters):
    for v in range(1, num_voters+1):
        try: # see if there's already a user with this id
            user = auth_models.User.get_by_type_and_id(user_type='password',
                                                       user_id=f'testuser{v}')
        except: # otherwise make a new user
            user = auth_models.User(user_type='password',
                                    user_id=f'testuser{v}')
            user.save()
        voter = Voter(uuid=str(uuid.uuid1()), user=user, election=election)
        voter.save()
    return

def generate_questions(num_questions, num_choices):
    question = {"answer_urls":[None for _ in range(num_choices)],
                "answers": [str(answer) for answer in range(num_choices)],
                "choice_type": "approval",
                "max": num_choices,
                "min": 0,
                "question": f"Choose your favorite numbers [0-{str(num_choices)})",
                "result_type": "absolute",
                "short_name": "choose",
                "tally_type": "homomorphic"}
    ballot = num_questions * [question]
    return ballot

def reset_questions(election):
    election.questions = []
    return

# The length of the outer list is how many ballot questions exist in the election
# For each ballot question, we have an inner list with the indices of the selected
# answers to that question.
def prepare_answers(num_questions, num_choices):
    answers = []
    for question in range(num_questions):
        # The questions lists 0, 1, ..., num_choices - 1 answers
        possible_answers = range(num_choices)
        # The voter can select between 0, 1, ..., num_choices answers
        number_answers_selected = random.randrange(num_choices + 1)
        # Generate a random subset of the possible answers, of length
        # number_answers_selected
        answers.append(random.sample(possible_answers, number_answers_selected))
    return answers