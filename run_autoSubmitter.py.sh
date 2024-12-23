#!/usr/bin/bash -l

#SBATCH --time=96:00:00
#SBATCH --mem=10g                                                                                  
#SBATCH --cpus-per-task=1




# needed for Athef because it didn't automatically source ~/.bashrc so couldn't conda activate anything
source /home/hsiehph/shared/bin/initialize_conda.sh

module purge

module load python3/3.10.9_anaconda2023.03_libmamba

./autoSubmitter.py

