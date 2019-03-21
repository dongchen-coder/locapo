import os
import matplotlib.pyplot as plt

path = "./poly_trace_lru/"
files = os.listdir(path)

figPath = "./plots/"

for f in files:
	content = open(path + f, "r")

	rdHist = {}
	totalCnt = 0

	for line in content:
		if ("BIN:" in line and "VAL:" in line and "COUNT:" in line):
			lineList = line.split()
			rd = int(lineList[3])
			cnt = int(lineList[5])
			if (cnt == 0):
				continue
			rdHist[rd] = cnt
			totalCnt += cnt

	content.close()
	#print rdHist
	#print totalCnt

	cacheSizes = []
	missRatios = []

	cacheSizes.append(0)
	missRatios.append(1)
	misses = totalCnt
	for key in sorted(rdHist.keys()):
		cacheSizes.append(key * 64 / 1024)
		misses -= rdHist[key]
		missRatios.append(float(misses)/totalCnt)

	plt.plot(cacheSizes, missRatios)
	plt.title(f.split('_')[0])
	plt.xlabel('Cache Sizes (KB)')
	plt.ylabel('Miss Ratios')
	plt.xscale('symlog')
	plt.savefig(figPath + f.split('_')[0] + '.pdf')
	plt.clf()

