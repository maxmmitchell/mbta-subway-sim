for gen in $(seq 4 $1);
do
for i in $(seq 1 $2);
do
    python3.9 main.py > model-gen$gen-$i.json
done
done