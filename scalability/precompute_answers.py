from modified_helios_objects import fromAnswer
from itertools import combinations
from tqdm import tqdm
import numpy as np
import pickle
import click

@click.command()
@click.option('--num_choices', '-c', type=int, required=True)
def main(num_choices):
    election_keypair = pickle.load(open("election_keypair.p", "rb"))
    choices = [i for i in range(num_choices)]
    print(f"Enumerating possible answers with {num_choices} choices")
    possible_answers = []
    for i in range(num_choices+1):
        possible_answers.extend([list(xs) for xs in combinations(choices, i)])
    
    print(f"Generating encyptions")
    encrypted_answers = [fromAnswer(choices, answer, election_keypair["public_key"], num_choices) for answer in tqdm(possible_answers)]
    np.save(f"encrypted_answers/all_answers_with_{num_choices}_choices.npy", encrypted_answers,  allow_pickle=True)
    return

if __name__=="__main__":
    main()