import sys
sys.path.append("../../helios-server/")
import helios.models as models
from helios_auth import models as auth_models
from helios.models import CastVote, Voter
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
    os.makedirs("outputs/", exist_ok=True)
    output_file = f"outputs/{num_voters}V_{num_questions}Q_{num_choices}C"
    if output_suffix:
        output_file += f"_{output_suffix}"
    output_file += ".csv"
    print(f"Saving results to {output_file}:")
    if not os.path.exists(output_file):
        with open(output_file, "a") as f:
            f.write("encrypt_time,tally_time,decrypt_time,total_time\n")
        f.close()

    # Load a user to be the admin (right now it's Ben, maybe could change?)
    overall_tic = time.perf_counter()
    # ben = auth_models.User.objects.get(user_id='ben@adida.net',
    #                                 user_type='google')

    # # Getting a pre-made election.
    # # This might be fully run and tallied/decrypted, so we'll reset things below
    # election, _ = models.Election.get_or_create(short_name='my_test',
    #                                             name='My Test',
    #                                             description='Please let this work....',
    #                                             admin=ben)

    # # ...generate some trustees (unnecessary to do again for 'my_test'):
    # # election.generate_trustee(views.ELGAMAL_PARAMS)

    # # Remove all voters from the election and strip out the questions:
    # delete_all_voters(election)
    # reset_questions(election)

    # # Add voters to the election
    # add_voters(election, num_voters)

    # # ...add some questions to the ballot:
    # questions = generate_questions(num_questions, num_choices)
    # election.save_questions_safely(questions)

    # # ...freeze the election (unecessary to do again for 'my_test'):
    # # election.freeze()

    # encrypt_time = 0
    # print("Encrypting votes...")
    # for voter in tqdm(Voter.get_by_election(election)):
    #     answers = prepare_answers(num_questions, num_choices)
    #     tic = time.perf_counter()
    #     vote = EncryptedVote.fromElectionAndAnswers(election, answers)
    #     toc = time.perf_counter()
    #     # assert vote.verify(election)
    #     castvote = CastVote(vote=vote, vote_hash=vote.hash, voter=voter)
    #     voter.store_vote(castvote)
    #     encrypt_time += toc - tic
    # with open(output_file, "a") as f:
    #     f.write(f"{encrypt_time:0.3f},")
    # f.close()

    election = models.Election.get_by_short_name(f'election_{num_questions}_questions_{num_choices}_choices_{num_trustees}_trustees_{num_voters}_voters')

    # Compute the tally!
    print("Tallying...")
    tic = time.perf_counter()
    election.compute_tally()
    toc = time.perf_counter()
    tally_time = toc - tic
    with open(output_file, "a") as f:
        f.write(f"{tally_time:0.3f},")
    f.close()

    # Decrypt the computed tally
    print("Decrypting...", end="")
    tic = time.perf_counter()
    election.helios_trustee_decrypt()
    election.combine_decryptions()
    toc = time.perf_counter()
    decrypt_time = toc - tic
    total_time = tic - overall_tic
    with open(output_file, "a") as f:
        f.write(f"{decrypt_time:0.3f},{total_time:0.3f}\n")
    f.close()
    print(" Done!")
    return

if __name__=="__main__":
    main()
    
