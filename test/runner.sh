#!/bin/bash
FILES="./test_*.py"
for f in $FILES
do
  echo "Running test: $f ..."

  ../build/micropython ./main.py ${f%.*}
done
