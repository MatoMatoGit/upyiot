#!/bin/bash
TEST=${1:-all}

echo "$TEST"

FILES="./test_*.py"

if [ $TEST = all ]; then
echo "Running all tests ..." 
for f in $FILES
do
  echo "Running test: ${f%.*} ..."

  ../build/micropython ./main.py ${f%.*}
done
else
echo "Running test: $TEST ..."
../build/micropython ./main.py ${TEST%.*}
fi

