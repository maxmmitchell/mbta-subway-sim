for i in $(seq 1 $1);
do
    python3.9 main.py > model-20240307-$i.json
done