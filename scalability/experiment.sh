# python -m cProfile -o test.cprof run_election.py -v 10 -q 2 -c 4 -s test
python prep_election.py -v 10 -q 4 -c 4 -s test
python run_election.py -v 10 -q 4 -c 4 -s test

# q=10
# c=5

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
