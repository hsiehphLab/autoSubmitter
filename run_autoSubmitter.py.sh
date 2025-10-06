#!/usr/bin/bash -l

#SBATCH --time=96:00:00
#SBATCH --mem=10g                                                                                  
#SBATCH --cpus-per-task=1




# needed for Athef because it didn't automatically source ~/.bashrc so couldn't conda activate anything
source /projects/standard/hsiehph/shared/bin/initialize_conda.sh

module purge
# fix (DG, 2025.10.03)
# the problem was that the module overrode the conda activate fastcn3_env
# needed by the mapping.smk rule of fastcn and thus it would fail.
# But autoSubmitter needs python.  biopython is just a way to get it python (any conda
# environment that had python would do)
#module load python3/3.10.9_anaconda2023.03_libmamba
conda activate biopython
# end

./autoSubmitter.py

