v=200
q=4
c=4

python -m cProfile -o 200V_4Q_4C_test_enc_verify.prof prep_election.py -v $v -q $q -c $c -s test_verify
python -m cProfile -o 200V_4Q_4C_test_verify.prof run_election.py -v $v -q $q -c $c -s test_verify


# for _ in 1 2 3 4 5
# do
#     python run_election.py -v 1000 -q 10 -c 5
# done

# for _ in 1 2 3 4 5
# do
#     python run_election.py -v 1000 -q 10 -c 10
# done

#for _ in 1 2 3 4 5
#do
#    python run_election.py -v 5 -q $q -c $c
#done

#for _ in 1 2 3 4 5
#do
#    python run_election.py -v 10 -q $q -c $c
#done

#for _ in 1 2 3 4 5
#do
#    python run_election.py -v 100 -q $q -c $c
#done
