from modified_helios_objects import OurTally, OurEncryptedVote
import numpy as np
import pickle
import click

@click.command()
@click.option('--num_questions', '-q', type=int, required=True)
@click.option('--num_choices', '-c', type=int, required=True)
@click.option('--num_voters', '-v', type=int, required=True)
def main(num_questions, num_choices, num_voters):
    election_keypair = pickle.load(open("election_keypair.p", "rb"))
    all_encrypted_answers = np.load(f"encrypted_answers/all_answers_with_{num_choices}_choices.npy",  allow_pickle=True)
    pk = election_keypair["public_key"]
    decryption_factors = election_keypair["decryption_factors"]

    tally = OurTally(num_questions=num_questions,
              num_choices=num_choices,
              pk=pk)

    for voter in range(num_voters):
        answers = [np.random.choice(all_encrypted_answers) for _ in range(num_questions)]
        print([answer.answer for answer in answers])
        vote = OurEncryptedVote.fromAnswers(answers)
        
        tally.add_vote(vote, verify_p=False)
    result = tally.decrypt_from_factors(decryption_factors, pk)
    print(result)
    return

if __name__=="__main__":
    main()