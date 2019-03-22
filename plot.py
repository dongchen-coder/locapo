import os
import matplotlib.pyplot as plt

lru_path = "./poly_trace_lru/"
files = os.listdir(lru_path)

lru_mrc_path = "./poly_trace_lru_mrc/"

rll_path = "./poly_trae_rll/"

figPath = "./plots/"

for f in files:
	
	#if ('mvt' not in f):
	#	continue

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
	#print rdHist
	#print totalCnt

	cacheSizes = []
	missRatios = []

	cacheSizes.append(0)
	missRatios.append(1)
	misses = totalCnt + coldMiss
	
	content = open(lru_mrc_path + f.replace("_trace_result", "_miss_ratio_curve"),"w")
	content.write("0 1\n")
	for key in sorted(rdHist.keys()):
		cacheSizes.append(float((key + 1) * 64) / 1024)
		misses -= rdHist[key]
		missRatios.append(float(misses)/totalCnt)
		content.write(str(float((key + 1) * 64) / 1024) + " " + str(float(misses)/totalCnt) + "\n")
	content.close()
	#print cacheSizes
	#print missRatios

	plt.plot(cacheSizes, missRatios)
	plt.title(f.split('_')[0])
	plt.xlabel('Cache Sizes (KB)')
	plt.ylabel('Miss Ratios')
	plt.xscale('symlog')
	plt.savefig(figPath + f.split('_')[0] + '.pdf')
	plt.clf()

