
#!/bin/bash

# run udpate command
bash ./update.command

# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
source ~/miniconda3/etc/profile.d/conda.sh
# <<< conda initialize <<<

# Activate the conda environment
conda activate hca

# # Command to start the backend
cd ~/development/hca && npm start &

# # Command to start the frontend
cd ~/development/hca_backend && python3 app.py



