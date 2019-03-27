import os
import matplotlib.pyplot as plt

lru_path = "./poly_trace_lru/"
files = os.listdir(lru_path)

lru_mrc_path = "./poly_trace_lru_mrc/"

rll_path = "./poly_trace_rll/"

rll_maxNumOfCLSize_path = "./poly_trace_rll_maxCLSize/"

figPath = "./plots/"

for f in files:

	# Reading and processing LRU results 
	content = open(lru_path + f, "r")

	rdHist = {}
	totalCnt = 0
	coldMiss = 0

	for line in content:
		if ("BIN:" in line and "VAL:" in line and "COUNT:" in line):
			lineList = line.split()
			rd = int(lineList[3])
			cnt = int(lineList[5])
			if (cnt == 0):
				continue
			rdHist[rd] = cnt
			totalCnt += cnt
		elif ("Total number of data blocks is" in line):
			lineList = line.split()
			coldMiss = int(lineList[7])

	content.close()

	cacheSizes = []
	missRatios = []

	cacheSizes.append(0)
	missRatios.append(1)

	totalCnt += coldMiss
	misses = totalCnt
	
	content = open(lru_mrc_path + f.replace("_trace_result", "_miss_ratio_curve"),"w")
	content.write("0 1\n")
	for key in sorted(rdHist.keys()):
		cacheSizes.append(float((key + 1) * 64) / 1024)
		misses -= rdHist[key]
		missRatios.append(float(misses)/totalCnt)
		content.write(str(float((key + 1) * 64) / 1024) + " " + str(float(misses)/totalCnt) + "\n")
	content.close()

	# Reading and processing RLL resutls
	cacheSizes_rll = []
	missRatios_rll = []
	if (os.path.exists(rll_path + f.replace("_trace_result.txt","") + "_ref_arr.cpp.o.tr.txt")):
		content = open(rll_path + f.replace("_trace_result.txt","") + "_ref_arr.cpp.o.tr.txt")
		for line in content:
			if ("Total costs (block)" in line):
				lineList = line.split()
				cacheSizes_rll.append(float(lineList[4]) * 64 / 1024)
			if ("Miss ratio" in line):
				lineList = line.split()
				missRatios_rll.append(float(lineList[2]))
		content.close()

	# Reading and processing RLL max number of CL size results
	maxCLSizes_rll = []
	if (os.path.exists(rll_maxNumOfCLSize_path + f.replace("_trace_result.txt","") + "_rll_maxCLSize.txt")):
		content = open(rll_maxNumOfCLSize_path + f.replace("_trace_result.txt","") + "_rll_maxCLSize.txt")
		for line in content:
			maxCLSizes_rll.append(float(line) * 64 / 1024)
		content.close()

	# Ploting the plots
	plt.plot(cacheSizes, missRatios, 'b', label = "LRU")
	plt.plot(cacheSizes_rll, missRatios_rll, 'r', label = "RLL")
	if (len(maxCLSizes_rll) == len(missRatios_rll)):
		plt.plot(maxCLSizes_rll, missRatios_rll, 'g', label = "RLL_MAX")
	plt.title(f.split('_')[0])
	plt.xlabel('Cache Sizes (KB)')
	plt.ylabel('Miss Ratios')
	plt.xscale('symlog')
	plt.legend()
	plt.savefig(figPath + f.split('_')[0] + '.pdf')
	plt.clf()

