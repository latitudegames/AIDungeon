#!/bin/bash
START=25
END=50
for ((I=0;I<END;I++));
do
	python3 main.py "$(($I * 2))" "$(( ($I + 1) * 2 ))" &
done
