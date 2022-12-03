# Imports
import sys
sys.path.append("..")
import helios.models as models
from helios_auth import models as auth_model
import helios.views as views
from itertools import combinations
from election_utils import generate_questions, add_voters
from helios.models import Voter
from helios.workflows.homomorphic import EncryptedVote
from tqdm import tqdm
import time
import click

@click.command()
@click.option("--num_choices", "-c", type=int, required=True)
@click.option("--num_questions", "-q", type=int, required=True)
def main(num_choices, num_questions):
    # Initialize election
    admin, _ = auth_model.User.objects.get_or_create(user_type='google',user_id='admin@admin.com', info={'name':'Election Admin'})
    short_name = f"verify_choices_{num_choices}_questions_{num_questions}"
    election, _ = models.Election.get_or_create(short_name=short_name,
                                                name=short_name,
                                                admin=admin)

    # Set up possible answers
    possible_answers = []
    choices = [i for i in range(num_choices)]
    for i in range(num_choices+1):
        possible_answers.extend([list(xs) for xs in combinations(choices, i)])
    num_voters = len(possible_answers)

    if election.frozen_at is None:
        # Authenticate trustee
        election.generate_trustee(views.ELGAMAL_PARAMS)

        # Add voters and questions to the election
        add_voters(election, num_voters)
        questions = generate_questions(num_questions, num_choices)
        election.save_questions_safely(questions)
        election.freeze()

    voters = Voter.get_by_election(election)
    encrypt_time = 0
    verify_time = 0
    begin = time.perf_counter()
    for i, voter in tqdm(enumerate(voters), total=len(voters)):
        answer = possible_answers[i]

        tic = time.perf_counter()
        vote = EncryptedVote.fromElectionAndAnswers(election, [answer for _ in range(num_questions)])
        toc = time.perf_counter()
        encrypt_time += toc - tic
        assert vote.verify(election)
        tac = time.perf_counter()
        verify_time += tac - toc
    end = time.perf_counter()
    
    print(f"Encrypted and verified all {num_voters} possible answers")
    print(f"Total Encryption Time: {encrypt_time}")
    print(f"Total Verification Time: {verify_time}")
    print(f"Total Time: {end-begin}")
    

if __name__=="__main__":
    main()


    

    