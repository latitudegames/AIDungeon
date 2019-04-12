#!/bin/bash
START=0
END=25
for ((I=0;I<END;I++));
do
	python3 main.py "$(($I * 2))" "$(( ($I + 1) * 2 ))" &
done
