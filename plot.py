import os
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

lru_path = "./poly_trace_lru/"
files = os.listdir(lru_path)

lru_mrc_path = "./poly_trace_lru_mrc/"

rll_path = "./poly_trace_rll/"

rll_maxNumOfCLSize_path = "./poly_trace_rll_maxCLSize/"

opt_path = "./poly_trace_opt_mrc/"

figPath = "./plots/"

fig = plt.figure(figsize=(6,8))
fig_cnt = 1

for f in files:

	if (".DS_Store" in f):
		continue

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
	print f.replace("_trace_result.txt","") + " missing : ",
	for i in range(len(cacheSizes_rll)):
		if (os.path.exists(rll_maxNumOfCLSize_path + f.replace("_trace_result.txt","") + "_lease_" + str(i) + "_rll_maxCLSize.txt")):
			content = open(rll_maxNumOfCLSize_path + f.replace("_trace_result.txt","") + "_lease_" + str(i) + "_rll_maxCLSize.txt")
			for line in content:
				maxCLSizes_rll.append(float(line) * 64 / 1024)
			content.close()
		else:
			print i,
	print ""

	#if ("gramschmidt" in f):
	#	for index in range(len(cacheSizes_rll)):
	#		print cacheSizes_rll[index], maxCLSizes_rll[index], missRatios_rll[index]

	# Reading OPT results
	cacheSizes_opt = []
	missRatios_opt = []
	if (os.path.exists(opt_path + "opt_" + f.replace("_trace_result.txt","") + ".cpp.o_mrc")):
		content = open(opt_path + "opt_" + f.replace("_trace_result.txt","") + ".cpp.o_mrc", 'r')
		for line in content:
			lineList = line.split()
			if (len(lineList) == 2):
				if (lineList[0].isdigit()):
					cacheSizes_opt.append(float(lineList[0]))
					missRatios_opt.append(float(lineList[1]))


	# Ploting the plots
	'''
	plt.plot(cacheSizes, missRatios, 'b', label = "LRU")
	plt.plot(cacheSizes_rll, missRatios_rll, 'r', label = "RLL")
	if (len(maxCLSizes_rll) == len(missRatios_rll)):
		plt.plot(maxCLSizes_rll, missRatios_rll, 'g', label = "RLL_MAX")
	plt.plot(cacheSizes_opt, missRatios_opt, 'y', label = "OPT")
	plt.title(f.replace("_trace_result.txt",""))
	plt.xlabel('Cache Sizes (KB)')
	plt.ylabel('Miss Ratios')
	plt.xscale('symlog')
	plt.legend()
	plt.savefig(figPath + f.split('_')[0] + '.pdf')
	plt.clf()
	'''
#e66101
#fdb863
#b2abd2
#5e3c99

	# Ploting to all.pdf
	ax = fig.add_subplot(10, 3, fig_cnt)
	ax.set_title(f.replace("_trace_result.txt",""), fontsize = 10, y = 0.6)
	l1 = ax.plot(cacheSizes, missRatios, '#5e3c99', linewidth=2.5, label = "LRU")[0]
	l2 = l1
	if (len(maxCLSizes_rll) == len(missRatios_rll)):
		l2 = ax.plot(maxCLSizes_rll, missRatios_rll, '#fdb863', linewidth=2, label = "ORL-MAX")[0]
	l3 = ax.plot(cacheSizes_rll, missRatios_rll, '#b2abd2', linewidth=1.5, label = "ORL-AVG")[0]
	l4 = ax.plot(cacheSizes_opt, missRatios_opt, '#e66101', linewidth=1, label = "OPT")[0]
	if (fig_cnt == 29):
		ax.set_xlabel('Cache Sizes (KB)')
	if (fig_cnt == 16):
		ax.set_ylabel('Miss Ratios')
	ax.set_xscale('symlog')
	#ax.xaxis.set_major_locator(plt.LogLocator())	
	#ax.xaxis.set_bounds(1)
	#ax.xaxis.set_xticklabels(exclude_overlapping=True)
	maxCacheSize = 1
	if (len(cacheSizes) != 0):
		maxCacheSize = max(cacheSizes[-1], maxCacheSize)
	if (len(maxCLSizes_rll) != 0):
		maxCacheSize = max(maxCLSizes_rll[-1], maxCacheSize)
	if (len(cacheSizes_opt) != 0):
		maxCacheSize = max(cacheSizes_opt[-1], maxCacheSize)
	numOfTicks = math.log10(maxCacheSize)
	showed_xticks = []
	for i in range(int(numOfTicks)):
		if (int(numOfTicks) >= 5 and i % 2 == 1):
			continue
		showed_xticks.append(math.pow(10, i))
	ax.set_xticks(showed_xticks)

	if (fig_cnt == 1):
		fig.legend([l1, l2, l3, l4], ["LRU", "ORL-MAX", "ORL-AVG", "OPT"], ncol=4, mode="expand", loc = "upper center")

	fig_cnt += 1

plt.tight_layout(pad=0.4, w_pad=0.4, h_pad=-1.2)
plt.subplots_adjust(left=0.08, right = 0.98, top = 0.95, bottom = 0.07)
#plt.show()
plt.savefig(figPath + "all.pdf")
