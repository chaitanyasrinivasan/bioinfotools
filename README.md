# bioinfotools

## Map Genes to Regulatory Elements

Files :
- `map_genes.sh`
- `get_gene_and_exon_coordinates.py`

Dependencies:
- [Python 3](https://docs.anaconda.com/anaconda/install/)
	- argparse
	- sys
- [bedtools](https://bedtools.readthedocs.io/en/latest/)
- [GENCODE Human Release 33](https://www.gencodegenes.org/human/release_33.html)
- [wget](https://www.gnu.org/software/wget/)

Description:

This script takes in single column CSV inputs with GENCODE human gene names and outputs BED format files corresponding to the noncoding (and by proxy, regulatory) regions flanking the genes. The program will create separate folders containing the following intermediate sets of regions for each input CSV: genes, exons, non-overlapping exons, 20 kb regions down- and up-stream of genes, introns, and introns merged with 20 kb flanking regions. The output can be defined as foreground genomic regions of interest for integrative GWAS enrichment analysis from transcriptomics data.

Usage:

```shell
bash map_genes.sh
```

## Classification of HeLa Subcellular Structure from Fluorescent Microscopy Images

Files:
- hela_svm.py
- HeLa_dataset/

Dependencies:
- [Python 3](https://docs.anaconda.com/anaconda/install/)
	- glob
	- os
	- sys
	- numpy
	- cv2
	- skimage
	- sklearn
- HeLa Subcellular Structure Dataset

Description:

This non-linear SVM classifier extracts Haralick texture features to produce a matrix of direction-specific descriptors for each image. These features include ASM, contrast, dissimilarity, homogeneity, energy, and correlation measured across the horizontal, vertical, and diagonal planes. The SVM achieves a classification accuracy of 0.96 on the test set.

Usage:

```python
python hela_svm.py
```

## Automated Cell Counter

File:
- count_cells.py

Dependencies:
- [Python 3](https://docs.anaconda.com/anaconda/install/)
	- glob
	- numpy
	- cv2
	- scipy


Description:

This program reads in PNG fluorescent microscopy images as 8-bit images and uses local adaptive thresholding to segment and automatically count the number of cells. The images are preprocessed using Gaussian blurring, and the sigma parameter for this filter can be tuned in accordance with the input image quality.

Usage:

```python
python count_cells.py
```
