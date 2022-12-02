import sys
sys.path.append("../../helios-server/")
import helios.models as models
from helios_auth import models as auth_models
from helios.models import CastVote, Voter, Trustee
from helios.workflows.homomorphic import EncryptedVote
from helios_auth import models as auth_model
from election_utils import *
from tqdm import tqdm
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
    os.makedirs("outputs/", exist_ok=True)
    output_file = f"outputs/{num_voters}V_{num_questions}Q_{num_choices}C_{num_trustees}T"
    if output_suffix:
        output_file += f"_{output_suffix}"
    output_file += ".csv"
    print(f"Saving results to {output_file}:")
    if not os.path.exists(output_file):
        with open(output_file, "a") as f:
            f.write("encrypt_time,tally_time,decrypt_time\n")
        f.close()

    short_name = f'election_{num_questions}_questions_{num_choices}_choices_{num_trustees}_trustees_{num_voters}_voters'
    admin, _ = auth_model.User.objects.get_or_create(user_type='google',user_id='admin@admin.com', info={'name':'Election Admin'})
    election, _ = models.Election.get_or_create(short_name=short_name,
                                                name=f'Election with {num_questions} Questions, {num_choices} Choices, {num_trustees} Trustees, and {num_voters} Voters',
                                                admin=admin)
    print(election.id)
    print("now election hash is: ", election.hash)
    # election.hash = "hghD9wfvvR1YkQQLNFPupr/fyJyFzNQly5Kdd0XTPfw"
    # print("now election hash is: ", election.hash)

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
    return

if __name__=="__main__":
    main()
    
