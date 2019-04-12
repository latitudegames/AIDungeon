#!/bin/bash
END=25
for ((I=0;I<END;I++));
do
	python3 main.py "$(($I * 4))" "$(( ($I + 1) * 4 ))" &
done
