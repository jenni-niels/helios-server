import sys
sys.path.append("../../helios-server/")
from modified_helios_objects import OurTally, OurEncryptedVote, generateFromAnswers
from helios.workflows.homomorphic import Tally, EncryptedVote
import helios.models as models
from helios.models import Trustee, CastVote, Voter
from helios_auth import models as auth_model
from election_utils import prepare_answers, add_voters, generate_questions
import helios.views as views
import numpy as np
import pickle
import click

@click.command()
@click.option('--num_questions', '-q', type=int, required=True)
@click.option('--num_choices', '-c', type=int, required=True)
@click.option('--num_voters', '-v', type=int, required=True)
def main(num_questions, num_choices, num_voters):
    # admin, _ = auth_model.User.objects.get_or_create(user_type='google',user_id='admin@admin.com', info={'name':'Election Admin'})
    num_trustees = 1
    short_name = f'election_{num_questions}_questions_{num_choices}_choices_{num_trustees}_trustees_{num_voters}_voters'
    # election, _ = models.Election.get_or_create(short_name=short_name,
    #                                             name=f'Election with {num_questions} Questions, {num_choices} Choices, {num_trustees} Trustees, and {num_voters} Voters',
    #                                             admin=admin)
    election = models.Election.get_by_short_name(short_name)
    # if election.frozen_at is not None:
    #     print("Election with this specification already exists")
    #     with open(output_file, "a") as f:
    #         f.write(f",")
    #     f.close()
    #     exit()

    # ## Currently only support 1.
    # for i in range(num_trustees):
    #     election.generate_trustee(views.ELGAMAL_PARAMS)
    
    # # Add voters to the election
    # add_voters(election, num_voters)

    # # ...add some questions to the ballot:
    # questions = generate_questions(num_questions, num_choices)
    # election.save_questions_safely(questions)

    # election.freeze()

    # tally = OurTally(num_questions=num_questions,
    #           num_choices=num_choices,
    #           pk=pk)
    tally = Tally(election=election)
    # tally.questions = 

    election_keypair = pickle.load(open("election_keypair.p", "rb"))
    all_encrypted_answers = np.load(f"encrypted_answers/all_answers_with_{num_choices}_choices.npy",  allow_pickle=True)
    # pk = election_keypair["public_key"]
    # decryption_factors = election_keypair["decryption_factors"]
    # pk = election.public_key
    # print(election.encrypted_tally)
    # election.helios_trustee_decrypt()
    # trustees = Trustee.get_by_election(election)
    # decryption_factors = [t.decryption_factors for t in trustees]
    # print(decryption_factors)

    # for voter in range(num_voters):
    for voter in Voter.get_by_election(election):
        # answers = [np.random.choice(all_encrypted_answers) for _ in range(num_questions)]
        # print([answer.answer for answer in answers])
        # Soooo answers are of different inner types, I think — is that anything?
        answers = prepare_answers(num_questions, num_choices)
        # vote = OurEncryptedVote.fromAnswers(answers)
        vote = EncryptedVote.fromElectionAndAnswers(election, answers)
        castvote = CastVote(vote, vote_hash=vote.hash, voter=voter)
        voter.store_vote(castvote)
        # vote = generateFromAnswers(answers)
        
        # tally.add_vote(vote, verify_p=True)
    election.compute_tally(verify_p=False)
    print("Decrypting...", end="")

    election.helios_trustee_decrypt()
    election.combine_decryptions()
    print(f"Decryption Verifies: {[t.verify_decryption_proofs() for t in Trustee.get_by_election(election)]}")

    # result = tally.decrypt_from_factors(decryption_factors, pk)
    # print(result)
    return

if __name__=="__main__":
    main()