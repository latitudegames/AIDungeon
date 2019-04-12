#!/bin/bash
END=20
for ((I=0;I<END;I++));
do
	python3 main.py "$(($I * 5))" "$(( ($I + 1) * 5 ))" &
done
