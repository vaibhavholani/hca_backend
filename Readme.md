# Code setup

## Python 3.9 Runtime Setup
```bash
# Create the conda enviornment paralle to (NOT INSIDE) directory where hca_backend is clones
conda create -p hca_venv python==3.9 -c conda-forge
conda activate ./hca_venv

# Install the Requreiments
cd hca_backend
pip install -r ./requirements.txt
```
## PSQL Setup

For the code to run, we need a PSQL Database setup with with relevant information added


