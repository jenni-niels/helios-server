import sys
sys.path.append("..")
import helios.models as models
from helios_auth import models as auth_model
from helios.models import CastVote, Voter, Trustee
import helios.views as views
from helios.workflows.homomorphic import EncryptedVote
from modified_helios_objects import OurEncryptedVote
from election_utils import *
from tqdm import tqdm
import numpy as np
import pickle
import click
import time
import os

@click.command()
@click.option('--num_voters', '-v', type=int)
@click.option('--num_questions', '-q', type=int)
@click.option('--num_choices', '-c', type=int)
@click.option('--num_trustees', '-t', type=int, default=1)
@click.option('--output_suffix', '-s', type=str)
def main(num_voters, num_questions, num_choices, num_trustees=1, output_suffix=""):
    print(f'Creating Election with {num_questions} Questions, {num_choices} Choices, {num_trustees} Trustees, and {num_voters} Voters')

    os.makedirs("outputs/", exist_ok=True)
    output_file = f"outputs/{num_voters}V_{num_questions}Q_{num_choices}C"
    if output_suffix:
        output_file += f"_{output_suffix}"
    output_file += ".csv"
    print(f"Saving results to {output_file}:")
    if not os.path.exists(output_file):
        with open(output_file, "a") as f:
            f.write("encrypt_time,tally_time,decrypt_time\n")
        f.close()
    
    admin, _ = auth_model.User.objects.get_or_create(user_type='google',user_id='admin@admin.com', info={'name':'Election Admin'})
    
    # Getting a pre-made election.
    # This might be fully run and tallied/decrypted, so we'll reset things below
    short_name = f'election_{num_questions}_questions_{num_choices}_choices_{num_trustees}_trustees_{num_voters}_voters'
    election, _ = models.Election.get_or_create(short_name=short_name,
                                                name=f'Election with {num_questions} Questions, {num_choices} Choices, {num_trustees} Trustees, and {num_voters} Voters',
                                                admin=admin)
    print("precomputed election hash is: ", election.hash)

    if election.frozen_at is not None:
        print("Election with this specification already exists")
        with open(output_file, "a") as f:
            f.write(f",")
        f.close()
        exit()

    ## Currently only support 1.
    for i in range(num_trustees):
        election.generate_trustee(views.ELGAMAL_PARAMS)

    # Add voters to the election
    add_voters(election, num_voters)


    # ...add some questions to the ballot:
    questions = generate_questions(num_questions, num_choices)
    election.save_questions_safely(questions)
    print(election.public_key)
    election.freeze()
    print(election.public_key)
    # Make the public key the same as the election on which we precomputed the encrypted votes
    election_keypair = pickle.load(open("election_keypair.p", "rb"))
    old_pk = election.public_key
    election.public_key = election_keypair['public_key']
    new_pk = election.public_key
    assert old_pk != new_pk

    # Make the use the same election hash (line 89) as the precomputed encrypted votes, I think (see extracting_crypto.ipynb)
    precomputed_hash = '52dVuxvPgNzorVKOS4c4duwrpVckhHGst79IUgejOEU'
    # election.hash = precomputed_hash
    print(election.id)
    print("precomputed election hash is: ", election.hash)
    print("precomputed election hash is: ", election.hash)

    # We also might need to make the decryption factors align? but the decryption passes...

    encrypt_time = 0
    all_encrypted_answers = np.load(f"encrypted_answers/all_answers_with_{num_choices}_choices.npy",  allow_pickle=True)
    print("Encrypting votes...")
    for voter in tqdm(Voter.get_by_election(election)):
        answers = prepare_answers(num_questions, num_choices)
        # answers = [np.random.choice(all_encrypted_answers) for _ in range(num_questions)]
        tic = time.perf_counter()
        vote = EncryptedVote.fromElectionAndAnswers(election, answers)
        # vote = OurEncryptedVote.fromAnswers(election, answers)
        toc = time.perf_counter()
        # assert vote.verify(election) # maybe comment out
        castvote = CastVote(vote=vote, vote_hash=election.hash, voter=voter)
        voter.store_vote(castvote)
        encrypt_time += toc - tic
    with open(output_file, "a") as f:
        f.write(f"{encrypt_time:0.3f},")
    f.close()
    print("precomputed election hash is: ", election.hash)

     # Compute the tally!
    print("Tallying...")
    tic = time.perf_counter()
    election.compute_tally(verify_p=True)
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
    print(f"Decryption Verifies: {[t.verify_decryption_proofs() for t in Trustee.get_by_election(election)]}")
    print(election.result)
    toc = time.perf_counter()
    decrypt_time = toc - tic
    with open(output_file, "a") as f:
        f.write(f"{decrypt_time:0.3f}\n")
    f.close()
    print(" Done!")
if __name__=="__main__":
    main()