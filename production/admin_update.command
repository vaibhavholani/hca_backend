#!/bin/bash

# run udpate command
bash ./update.command

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
source ~/miniconda3/etc/profile.d/conda.sh
# <<< conda initialize <<<

# Activate the conda environment
conda activate hca

# Command to resintall packages from requirements.txt
# cd ~/development/hca_backend && pip3 install -r requirements.txt


# # Command to start the frontend
cd ~/development/hca_backend/production && python3 custom_updates.py
