import sys
sys.path.append("../../helios-server/")
from helios.workflows.homomorphic import Tally, EncryptedVote, DLogTable
import numpy as np
import pickle
from tqdm import trange
import time
import click
import os

def decrypt_and_prove(tally, sk):
    """
    Takes a tally and the corresponding secret key
    Returns an array of tallies and a corresponding array of decryption proofs.
    """
    dlog_table = DLogTable(base = tally.public_key.g, modulus = tally.public_key.p)
    dlog_table.precompute(tally.num_tallied)

        
    # for all choices of all questions (double list comprehension)
    decrypted_tally = []
    decryption_proof = []

    for question_num in range(len(tally.questions)):
        question = tally.questions[question_num]
        answers = question['answers']
        question_tally = []
        question_proof = []

        for answer_num in range(len(answers)):
            # do decryption and proof of it
            plaintext, proof = sk.prove_decryption(tally.tally[question_num][answer_num])

            # look up appropriate discrete log
            question_tally.append(dlog_table.lookup(plaintext))
            question_proof.append(proof)
        
        decrypted_tally.append(question_tally)
        decryption_proof.append(question_proof)

    return decrypted_tally, decryption_proof

@click.command()
@click.option('--num_questions', '-q', type=int, required=True)
@click.option('--num_choices', '-c', type=int, required=True)
@click.option('--num_voters', '-v', type=int, required=True)
def main(num_questions, num_choices, num_voters):

    os.makedirs("outputs", exist_ok=True)
    output_file = f"outputs/tally_decrypt.csv"

    print(f"Saving results to {output_file}:")
    if not os.path.exists(output_file):
        with open(output_file, "a") as f:
            f.write("num_voters,num_questions,num_choices,tally_time,decrypt_time\n")
    

    keys = pickle.load(open("EGkeypair.p", "rb"))
    encrypted_answers = np.load(f"encrypted_answers/all_answers_with_{num_choices}_choices.npy",  allow_pickle=True)
    tally = Tally()

    tally.questions = {q: {"answers": range(num_choices)} for q in range(num_questions)}
    tally.public_key = keys.pk
    tally.tally = [[0 for _ in range(num_choices)] for _ in tally.questions]

    print("Tallying...")
    tic = time.perf_counter()
    for _ in trange(num_voters):
        vote = EncryptedVote()
        vote.encrypted_answers = np.random.choice(encrypted_answers, num_questions)
        tally.add_vote(vote, verify_p=False)
    toc = time.perf_counter()
    tally_time = toc - tic
    with open(output_file, "a") as f:
        f.write(f"{num_voters},{num_questions},{num_choices},")
        f.write(f"{tally_time:0.3f},")


    print("Decrypting...")
    tic = time.perf_counter()
    result = decrypt_and_prove(tally, keys.sk)
    toc = time.perf_counter()
    decrypt_time = toc - tic
    with open(output_file, "a") as f:
        f.write(f"{decrypt_time:0.3f}\n")
    print("Tally Results:")
    print(result[0])


if __name__=="__main__":
    main()