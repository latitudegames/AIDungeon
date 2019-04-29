#!/bin/bash

START=80
END=100
for ((I=START;I<END;I++));
do
	python3 main.py "$(($I * 1))" "$(( ($I + 1) * 1 ))" &
done
