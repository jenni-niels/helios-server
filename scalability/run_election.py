import sys
sys.path.append("../../helios-server/")
import helios.models as models
from helios_auth import models as auth_models
from helios.models import CastVote, Voter
from helios.workflows.homomorphic import EncryptedVote
import time


# Load a user (right now it's Ben, maybe could change?)
ben = auth_models.User.objects.get(user_id='ben@adida.net',
                                   user_type='google')


# Getting a pre-made election.
# This will actually be fully run and tallied/decrypted
election, _ = models.Election.get_or_create(short_name='my_test',
                                            name='My Test',
                                            description='Please let this work....',
                                            admin=ben)

# If this were a new election, we'd have to do the following...
# ...register at least one voter in it:
# models.Voter.register_user_in_election(user, election)

# ...generate some trustees:
# election.generate_trustee(views.ELGAMAL_PARAMS)

# ...add some questions to the ballot:
questions = [{"answer_urls":[None, None, None],
              "answers": ["A", "B", "C"],
              "choice_type": "approval",
              "max": 1,
              "min": 1,
              "question": "A, B, or C?",
              "result_type": "absolute",
              "short_name": "W?",
              "tally_type": "homomorphic",
             }]
# election.save_questions_safely(questions)

# ...freeze the election:
# election.freeze()

# ...prepare at least one vote:
# The length of the outer list is how many ballot questions exist in the election
# For each ballot question, we have an inner list with the indices of the selected
# answers to that question. This one shows that there was one question, and the
# voter selected the answer in index 2 (in this case, 'C').
print("Encrypting vote...")
vote = EncryptedVote.fromElectionAndAnswers(election, [[2]])
assert vote.verify(election)

# ...store a cast vote with a registered voter, hence applying it to the election
voter = Voter.get_by_user(ben)[0] # possibly some better ways to do this...
print("Casting vote...")
castvote = CastVote(vote=vote,
                    vote_hash=vote.hash,
                    voter=voter)
voter.store_vote(castvote)

# Compute the tally!
print("Computing tally...")
tic = time.perf_counter()
election.compute_tally()
toc = time.perf_counter()
tally_time = toc - tic
print(f"Tallying time: {tally_time:0.4f}s")

# Decrypt the computed tally
print("Decrypting...")
tic = time.perf_counter()
election.helios_trustee_decrypt()
election.combine_decryptions()
toc = time.perf_counter()
decrypt_time = toc - tic
print(election.result)
print(f"Decrypting time: {decrypt_time:0.4f}s")