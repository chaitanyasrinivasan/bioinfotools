import sys
import argparse 

#Chaitanya Srinivasan
#input: single column of genes in .csv file
#output: gene and exon coordinates for each gene in the file
#dependencies: gencode v33 annotation must be in the same folder

def get_coords(geneMarker):
	geneoutfile = geneMarker[:-4]+"_genes.bed"
	exonoutfile = geneMarker[:-4]+"_exons.bed"
    # create a dictionary of gencode annotation
	with open("gencode.v33.annotation.gff3", 'r') as f, open(geneMarker, 'r') as g, open(geneoutfile, 'w') as h, open(exonoutfile, 'w') as e:
		geneCoordinates = dict()
		exonCoordinates = dict()
		for linef in f:
			if (linef[0] != "#"):
				genef = linef.split("\t")
				if (genef[2] == "gene"):
					chrf = genef[0]
					startf = genef[3]
					stopf = genef[4]
					geneInfof = genef[8].split(";")
					geneNamef = geneInfof[3].split("=")[1]
					geneCoordinates[str(geneNamef)] = (str(chrf),str(startf),str(stopf))
				elif (genef[2] == "exon"):
					chrf = genef[0]
					startf = genef[3]
					stopf = genef[4]
					geneInfof = genef[8].split(";")
					geneNamef = geneInfof[5].split("=")[1]
					if (geneNamef in exonCoordinates): #build a list of exonic coordinates for each gene
						exonCoordinates[str(geneNamef)].append([str(chrf),str(startf),str(stopf)])
					else:
						exonCoordinates[str(geneNamef)] = [[str(chrf),str(startf),str(stopf)]]
		lines = g.readlines()
		for lineg in lines:
			geneNameg = lineg.strip("\n")
			# cross reference gene with gencode annotation
			if (geneNameg in geneCoordinates):
				info = geneCoordinates[str(geneNameg)]
				if (info[0] != "X" and info[0] != "Y"):
					h.write(info[0]+"\t"+info[1]+"\t"+info[2]+"\t"+geneNameg+"\n")
			if (geneNameg in exonCoordinates):
				infoList = exonCoordinates[str(geneNameg)]
				for i in range(len(infoList)):
					if (infoList[i][0] != "X" and infoList[i][0] != "Y"):
						e.write(infoList[i][0]+"\t"+infoList[i][1]+"\t"+infoList[i][2]+"\t"+geneNameg+"\n")
f.close()
g.close()
h.close()
e.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--input", type=str, help="Input set of genes")

	options, args = parser.parse_known_args()

	if (len(sys.argv)==1):
	    parser.print_help(sys.stderr)
	    sys.exit(1)
	elif (options.input is None):
		parser.print_help(sys.stderr)
		sys.exit(1)
	else:
		get_coords(options.input)

