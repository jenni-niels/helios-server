## Parallelization ideals for Vote Verification/Tallying

Since decyption is fast we focus speeds ups on verfication and tally

In order to take advance of many parallel compute node we cannot assume that any given node is trustworthy and accurately reports the work it was assigned

Consider the following recursive approach given a range of encypted votes in some shared filestructure

```python

def verify_and_tally_votes(branching_factor, vote_id_range, public_crypto_params):
    if len(vote_id_range) <= branching_factor:
        vote_verifications = verify_votes(vote_id_range, public_crypto_params)
        running_tally = tally(filter(vote_id_range, vote_verifications))

        return proof_of_tally_accurate_to_valid_votes()
    else:
        verification_tally_pairs = [verify_and_tally_votes(branching_factor, 
                                                           sub_vote_id_range, 
                                                           public_crypto_params)       
                                     parrallel for sub_vote_id_range in divide(vote_id_range, branching_factor)]

        verifications, tallies = unzip(verification_tally_pairs)
        running_tally = tally(tallies)
        return (proof_of_prior_verifications_and_running_tally(), running_tally)

```