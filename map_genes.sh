#!/bin/bash

#Chaitanya Srinivasan
#usage : bash map_genes.sh

#purpose : map genes to regions that likely capture regulatory activity
#(intronic and intergenic coordinates)

#assumptions: list(s) of genes is a single column *.csv file in the
#current directory

#dependencies: bedtools, gencode v33 annotation and hg38 chrom sizes in
#the current directory

#output: .bed files in introns_and_flanks/

#CHECK DEPENDENCIES
if [ -x "$(command -v bedtools)" ]
then
  echo "Error: bedtools not executable"
  exit 1
fi
if [ ! -f gencode.v33.annotation.gff3 ]
then
  wget -nc ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_33/gencode.v33.annotation.gff3.gz
  gunzip gencode.v33.annotation.gff3.gz
fi
wget -nc http://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.chrom.sizes

# create output folders
mkdir -p genes exons exons_merged genes_20KBflank introns introns_and_flanks

#GET GENE AND EXON COORDINATES
echo "Mapping gene names to gene and exon coordinates..."

for file in *.csv;
do
	python get_gene_and_exon_coordinates.py -i $file
  # outputs gene and exon coordinate bed files for each gene list
done
mv *genes.bed genes/
mv *exons.bed exons/

#MERGE, SUBTRACT EXONS FROM GENE, AND FLANK GENE 20KB
echo "Merging exons..."

for file in exons/*_exons.bed;
do
	bedtools sort -i $file | bedtools merge -i stdin > "${file::-4}_merged.bed"
  # outputs merged exon bed coordinates
done
mv exons/*_merged.bed exons_merged/

echo "Subtracting merged exons from gene and getting gene flanks..."

i=0
for file in genes/*_genes.bed;
do
	genes[$i]=$file
	((i++))
done
i=0
for file in exons_merged/*_exons_merged.bed;
do
	exons[$i]=$file
	((i++))
done
arraylength=${#genes[@]}
for ((i=0; i<${arraylength}; i++));
do
	bedtools sort -i ${genes[i]} > "${genes[i]::-4}_sorted.bed"
	bedtools subtract -a "${genes[i]::-4}_sorted.bed" -b ${exons[i]}  > "${genes[i]::-9}introns.bed"
	# outputs introns
  	bedtools flank -i "${genes[i]::-4}_sorted.bed" -g hg38.chrom.sizes -b 20000 | bedtools subtract -a stdin -b "${genes[i]::-4}_sorted.bed" > "${genes[i]::-4}_20KBflank.bed"
  	# outputs 20 kilobase flanking regions from genes
done
rm genes/*genes_sorted.bed
mv genes/*introns.bed introns/
mv genes/*_20KBflank.bed genes_20KBflank/

#ADD GENE FLANKS TO INTRONS

echo "Adding gene flanks to introns..."

i=0
for file in genes_20KBflank/*_20KBflank.bed;
do
	flanks[$i]=$file
	((i++))
done
i=0
for file in introns/*_introns.bed;
do
	introns[$i]=$file
	((i++))
done
arraylength=${#flanks[@]}
for ((i=0; i<${arraylength}; i++));
do
	cat ${flanks[i]} ${introns[i]} | bedtools sort -i stdin | bedtools merge -i stdin > "${introns[i]::-4}_and_flanks.bed"
  #outputs merged intronic and intergenic regions
done
mv introns/*_and_flanks.bed introns_and_flanks/

echo "Done."
