import sys
sys.path.append("..")
import helios.models as models
from helios_auth import models as auth_model
from helios.models import CastVote, Voter
import helios.views as views
from helios.workflows.homomorphic import EncryptedVote
from election_utils import *
from tqdm import tqdm
import click
import time
import os

@click.command()
@click.option('--num_voters', '-v', type=int)
@click.option('--num_questions', '-q', type=int)
@click.option('--num_choices', '-c', type=int)
@click.option('--num_trustees', '-t', type=int)
@click.option('--output_suffix', '-s', type=str)
def main(num_voters, num_questions, num_choices, num_trustees=1, output_suffix=""):
    print(f'Creating Election with {num_questions} Questions, {num_choices} Choices, {num_trustees} Trustees, and {num_voters} Voters')
    admin = auth_model.User.objects.create(user_type='google',user_id='admin@admin.com', info={'name':'Election Admin'})

    # Getting a pre-made election.
    # This might be fully run and tallied/decrypted, so we'll reset things below
    election, _ = models.Election.get_or_create(short_name=f'election_{num_questions}_questions_{num_choices}_choices_{num_trustees}_trustees_{num_voters}_voters',
                                                name=f'Election with {num_questions} Questions, {num_choices} Choices, {num_trustees} Trustees, and {num_voters} Voters',
                                                admin=admin)

    if election.frozen_at is not None:
        print("Election With theses specifications already exits")
        exit()

    ## Cu
    for _ in range(num_trustees):
        election.generate_trustee(views.ELGAMAL_PARAMS)
    
    # Add voters to the election
    add_voters(election, num_voters)

    # ...add some questions to the ballot:
    questions = generate_questions(num_questions, num_choices)
    election.save_questions_safely(questions)

    encrypt_time = 0
    print("Encrypting votes...")
    for voter in tqdm(Voter.get_by_election(election)):
        answers = prepare_answers(num_questions, num_choices)
        tic = time.perf_counter()
        vote = EncryptedVote.fromElectionAndAnswers(election, answers)
        toc = time.perf_counter()
        # assert vote.verify(election)
        castvote = CastVote(vote=vote, vote_hash=vote.hash, voter=voter)
        voter.store_vote(castvote)
        encrypt_time += toc - tic
    print(f"{encrypt_time:0.3f},")

    election.freeze()