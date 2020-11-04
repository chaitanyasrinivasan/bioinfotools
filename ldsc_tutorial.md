# LDSC Regression Pipeline Tutorial

## Installation

1.	Installing ldsc (one time only)

```
git clone https://github.com/bulik/ldsc.git
cd ldsc
conda env create --file environment.yml
```
2. Activate LDSC conda environment

```
source activate ldsc
```

3. Test the installation

```
./ldsc.py -h
./munge_sumstats.py -h
```

4. Add ldsc to your `~/.bash_profile`

```
export PATH=/home/usr/path/to/ldsc:${PATH}
```

## Usage

Running LD-Score regression using hg38(GRCh38) genome coordinates. Note that reference files were generated using two different snplist files, and errors in GWAS/foreground enrichment might be from mismatched files using different snplists. Some annotated LD scores of different foregrounds, backgrounds, and GWAS enrichments can be found organized in the following directory for easy access for Pfenning lab members: `/projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments`

1. In parallel, create annotations and compute LD scores for a set of bed files corresponding to a set of foreground peaks enriched for SNPs in 1000G European Phase 3. `background.bed` corresponds to a broad set of peaks that is comparable to the foreground measurements. (Ex: Use Honeybadger2 for open chromatin foregrounds, RoadMap H3K27ac for H3K27ac foregrounds, etc.)

```shell
#!/bin/bash

cd /path/to/project/
mkdir -p annotations enrichments annotations/ProjectName

# submit annotate and compute jobs for each foreground, for each chromosome 1-22
for file in *.bed;
do
  sbatch --partition pool1 /projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments/scripts/annotate_bed_LDSC_hg38.sh -i $file -n "ProjectName_${file::-4}" -o annotations/ProjectName/
done

# merging all foregrounds with an appropriate background
cat *.bed background.bed | awk '{print $1, $2, $3}’ | perl -p -i -e 's/ /\t/g’ | bedtools sort -i stdin | bedtools merge -i stdin > background_ProjectName.bed

# submit annotation and LD computation jobs for each chromosome of the background peaks
sbatch --partition pfen_bigmem /projects/pfenninggroup/ machineLearningForComputationalBiology/gwasEnrichments/scripts/annotate_bed_LDSC_hg38.sh -i background_ProjectName.bed -n background_ProjectName -o annotations/ProjectName/
```

To run the pipeline using the hg19(GRCh37) reference, substitute the following plink and hapmap files in `/projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments/scripts/annotate_bed_LDSC_hg38.sh`:

```
/home/eramamur/resources/1000G_EUR_Phase3_plink/1000G.EUR.QC.${i}.bim
/home/eramamur/resources/hapmap3_snps/hm.${i}.snp    
```
2. Create a `.ldcts` file in which each line contains the foreground name, path to the cell type annotations and LD scores, and the path to the background annotations and LD scores. The cell type name and its path are separated by a single space. The path to the cell type and background annotations and LD scores are separated by a comma. Ensure that the `.ldcts` file does not contain any extra spaces so LDSC can parse the file paths correctly. Here is an example:

```
foreground1,/path/to/project/annotations/ProjectName/ProjectName_foreground1.,/path/to/project/annotations/ProjectName/background_ProjectName.
foreground2,/path/to/project/annotations/ProjectName/ProjectName_foreground2.,/path/to/project/annotations/ProjectName/background_ProjectName.
...
```

3. Prepare GWAS file for input using the following commands (assuming raw GWAS summary statistic file is in `/path/to/gwas.txt`)

```
srun --mem 4G --ntasks-per-core 1 -t 5-0 -p pfen_bigmem --pty /bin/bash 
source activate ldsc
python munge_sumstats.py --sumstats /path/to/gwas.txt --merge-alleles /projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments/1000G_EUR_Phase3_GRCh38_files/hapmap3_snps/w_hm3.noMHC.snplist --out /new/path/to/GWASName-Author_Year
```

To run the pipeline using the hg19(GRCh37) reference, provide the following file as an argument to `--merge-alleles`:

```
/projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments/1000G_EUR_Phase3_GRCh38_files/hapmap3_snps/w_hm3.snplist
```

This step creates new GWAS summary statistics file named `/new/path/to/gwas.sumstats.gz` in a format acceptable to the LDSC pipeline. Maintain a list of munged GWAS `/new/path/to/gwas.sumstats.gz` paths in `/projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments/gwas_list_sumstats.txt`. A collection of GWAS sumstats files that have been munged are located at `/projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments/gwas/munged`. Please contribute new GWAS sumstats files to this folder for everyone to use.

4. Create and submit a sbatch (.sb) script to run LD score regression on all foregrounds specified in the .ldcts file:

```
#!/bin/bash
#SBATCH -n 1
#SBATCH --partition=pfen_bigmem
#SBATCH --job-name=ldsc_ProjectName
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=10G
#SBATCH --error=run_enrich_ProjectName_%A_%a.err.txt
#SBATCH --output=run_enrich_ProjectName _%A_%a.out.txt
#SBATCH --array=1-18

source activate ldsc

# get the GWAS for this array job
GWAS=$(awk "NR==${SLURM_ARRAY_TASK_ID}" gwas_list_sumstats.txt)
GWAS_Label=$(basename $GWAS | sed 's/.sumstats.gz//g')
OUTDIR=/path/to/project/enrichments

# run LD score regression to get tissue enrichments
ldsc.py \
	--ref-ld-chr /projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments/1000G_EUR_Phase3_GRCh38_files/baseline_v1.2/baseline. \
	--w-ld-chr /projects/pfenninggroup/machineLearningForComputationalBiology/gwasEnrichments/1000G_EUR_Phase3_GRCh38_files/weights/weights.hm3_noMHC. \
	--ref-ld-chr-cts ProjectName.ldcts \
	--h2-cts $GWAS \
	--out $OUTDIR/ProjectName_${GWAS_Label}

```

To run the pipeline using the hg19(GRCh37) reference, provide the following files as arguments to `--ref-ld-chr` and `/path/to/weights`, respectively:

```
/home/eramamur/resources/1000G_EUR_Phase3_baseline/baseline.
/home/eramamur/resources/weights_hm3_no_hla/weights.

```

This creates an output files named `/path/to/ProjectName_GWAS.cell_type_results.txt` that contain the results of the cell type association analysis including p-values (unadjusted for multiple hypothesis correction), effect sizes and standard error.

5. Deactivate the ldsc environment

```
conda deactivate
```

6. Perform multiple hypothesis correction across all pairings of GWAS-cell type enrichments and plot the adjusted values.
