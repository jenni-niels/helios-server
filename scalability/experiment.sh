
q=10
c=10

for _ in 1 2 3 4 5
do
    python run_election.py -v 1 -q $q -c $c
done

for _ in 1 2 3 4 5
do
    python run_election.py -v 5 -q $q -c $c
done

for _ in 1 2 3 4 5
do
    python run_election.py -v 10 -q $q -c $c
done

for _ in 1 2 3 4 5
do
    python run_election.py -v 100 -q $q -c $c
done