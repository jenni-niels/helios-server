import sys
sys.path.append("../../helios-server/")
import helios.models as models
from helios_auth import models as auth_models
from helios.models import CastVote, Voter
from helios.workflows.homomorphic import EncryptedVote
from election_utils import *
import pandas as pd
import time


# Load a user to be the admin (right now it's Ben, maybe could change?)
ben = auth_models.User.objects.get(user_id='ben@adida.net',
                                   user_type='google')


# Getting a pre-made election.
# This might be fully run and tallied/decrypted, so we'll reset things below
election, _ = models.Election.get_or_create(short_name='my_test',
                                            name='My Test',
                                            description='Please let this work....',
                                            admin=ben)

# ...generate some trustees (unnecessary to do again for 'my_test'):
# election.generate_trustee(views.ELGAMAL_PARAMS)

# Remove all voters from the election and strip out the questions:
delete_all_voters(election)
reset_questions(election)

# Add voters to the election
N = 1
add_voters(election, N)

# ...add some questions to the ballot:
num_questions = 2
num_choices = 4
questions = generate_questions(num_questions, num_choices)
election.save_questions_safely(questions)

# ...freeze the election (unecessary to do again for 'my_test'):
# election.freeze()

tic = time.perf_counter()
encrypting_time = 0
asserting_time = 0
storing_time = 0
for voter in Voter.get_by_election(election):
    print(f"For voter: {voter.voter_id}...")
    answers = prepare_answers(num_questions, num_choices)
    for q, answer in enumerate(answers):
        print(f" -- Q{q}: {answers[q]}")
    enc_tic = time.perf_counter()
    vote = EncryptedVote.fromElectionAndAnswers(election, answers) # ~500ms
    enc_toc = time.perf_counter()
    assert vote.verify(election) # ~500ms
    ass_toc = time.perf_counter()
    castvote = CastVote(vote=vote, vote_hash=vote.hash, voter=voter)
    voter.store_vote(castvote)
    store_toc = time.perf_counter()
    encrypting_time += enc_toc - enc_tic
    asserting_time += ass_toc - enc_toc
    storing_time += store_toc - ass_toc
toc = time.perf_counter()
voting_time = toc - tic
print(f"Voting time: {voting_time:0.3f}s")
print(f"Encrypting time: {encrypting_time:0.3f}s")
print(f"Asserting time: {asserting_time:0.3f}s")
print(f"Storing time: {storing_time:0.3f}s")

# Compute the tally!
tic = time.perf_counter()
election.compute_tally()
toc = time.perf_counter()
tally_time = toc - tic
print(f"Tallying time: {tally_time:0.3f}s")

# Decrypt the computed tally
tic = time.perf_counter()
election.helios_trustee_decrypt()
election.combine_decryptions()
toc = time.perf_counter()
decrypt_time = toc - tic
print(f"Decrypting time: {decrypt_time:0.3f}s")
print(election.result)
