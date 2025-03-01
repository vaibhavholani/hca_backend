#!/bin/bash

# Run update command
bash ./update.sh

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
source ~/miniconda3/etc/profile.d/conda.sh
# <<< conda initialize <<<

# Activate the conda environment located at the specified path
conda activate /Users/vaibhavholani/development/business/hca_venv

# Command to start the backend
cd /Users/vaibhavholani/development/business/holani_cloth_agency/backend && python3 app.py
