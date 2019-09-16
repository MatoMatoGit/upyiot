#!/bin/bash
FILES="./test_*.py"
for f in $FILES
do
  echo "Processing $f file..."

  ../build/micropython ./main.py ${f%.*}
done
