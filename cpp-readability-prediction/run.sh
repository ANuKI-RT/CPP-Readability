#!/usr/bin/env bash
python readability_for_c/cli.py crawl -i /Users/duc/Downloads/rodos -o ./snippets/rodos -gf SampleKeyword -gm SampleKeyword2
python readability_for_c/cli.py metrics -i ./snippets -o metrics.csv
python readability_for_c/cli.py readability -i ./snippets -o readability.csv -m open_source -fs bw
python readability_for_c/cli.py extract-readability -i $HOME/Downloads/rodos -o readability.csv  -m open_source -fs bw
