#!/bin/bash
# Job name
#SBATCH --job-name=GPU_biobert_large_corpus_binary_combined

# Email job progress
#SBATCH --mail-type=ALL
#SBATCH --mail-user=mayla.boguslav@cuanschutz.edu 


# Resource allocation
#SBATCH -p titan
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=24gb
#SBATCH --gres=gpu
#SBATCH --time=60:00:00

# Log errors here:
#SBATCH --error=/Users/mabo1182/Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/eo/GPU_biobert_binary_combined_%j.err
#SBATCH --output=/Users/mabo1182/Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/eo/GPU_biobert_binary_combined_%j.out


cd /Users/mabo1182/Ignorance-Question-Work-Full-Corpus/Word_Analysis/BioBERT_Classification/biobert
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH 
export PATH=/usr/local/cuda/bin:$PATH
date
./fiji_run_biobert_all_onts_combined_binary.sh
date

