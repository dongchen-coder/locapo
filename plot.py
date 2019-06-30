import os
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

lru_path = "./poly_trace_lru_2/"
files = os.listdir(lru_path)

lru_mrc_path = "./poly_trace_lru_mrc_2/"

rll_path = "./poly_trace_rll/"

rll_maxNumOfCLSize_path = "./poly_trace_rll_maxCLSize/"

rll_cappedMaxNumOfCLSize_path = "./poly_trace_rll_CLSizes/"

opt_path = "./poly_trace_opt_mrc/"

figPath = "./plots/"

fig = plt.figure(figsize=(6,8))
fig_cnt = 1

yMax = {"mvt" : 0.3, "3mm" : 0.4, "bicg" : 0.1, "gemm" : 0.5, "heat_3d" : 0.2, "trmm" : 0.8, "covariance" : 1, "durbin" : 0.2, "doitgen" : 1, "deriche" : 0.4, "symm" : 0.7, "syr2d" : 0.6, "jacobi_2d" : 0.3, "adi" : 0.3, "gramschmidt" : 1, "gesummv" : 0.1, "correlation" : 0.8, "floyd_warshall" : 0.1, "atax" : 0.2, "ludcmp" : 0.8, "seidel_2d" : 0.1, "trisolv" : 0.2, "gemver" : 0.2, "fdtd_2d" : 0.2, "2mm" : 0.5, "jacobi_1d" : 0.2, "cholesky" : 0.2, "lu" : 0.5, "syrk" : 0.2, "nussinov" : 0.4}

#names = ["cholesky", "correlation", "floyd_warshall", "gramschmidt", "lu", "ludcmp", "nussinov", "symm", "syr2d", "trmm"]
names = []
sorted_names = []
for f in sorted(files):
	name = f.replace("_trace_result.txt","")
	if (name not in names):
		sorted_names.append(name)
sorted_names += sorted(names)



#for f in sorted(files):
for name in sorted_names:
	#print name
	f = name + "_trace_result.txt"

	if (".DS_Store" in f):
		continue

	#if ("doitgen" in f or "covariance" in f):
	#	continue

	# Reading and processing LRU results 
	content = open(lru_path + f, "r")

	rdHist = {}
	totalCnt = 0
	coldMiss = 0

	for line in content:
		'''
		if ("BIN:" in line and "VAL:" in line and "COUNT:" in line):
			lineList = line.split()
			rd = int(lineList[3])
			cnt = int(lineList[5])
			if (cnt == 0):
				continue
			rdHist[rd] = cnt
			totalCnt += cnt
		'''
		if ("Bin" in line and "Distance" in line and "Reuses" in line):
			lineList = line.split()
			#print lineList
			rd = int(lineList[4])
			if ("to" in line):
				rd = int(lineList[6])
			
			if ("to" in line):
				cnt = int(lineList[9])
			else:
				cnt = int(lineList[7])
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
		if (len(cacheSizes) != 0):
			cacheSizes.append(float((key) * 64) / 1024)
			missRatios.append(missRatios[-1])
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

	# Reading and processing RLL capped results
	maxCLSizes_capped_rll = []
	missRatios_capped_rll = []
	for i in range(len(cacheSizes_rll)):
		if (os.path.exists(rll_cappedMaxNumOfCLSize_path + f.replace("_trace_result.txt","") + "_lease_" + str(i) + "_rll_CLSize.txt")):
			content = open( rll_cappedMaxNumOfCLSize_path + f.replace("_trace_result.txt","") + "_lease_" + str(i) + "_rll_CLSize.txt", 'r')
			total_cnt = 0.0
			acc_cnt = 0.0
			for line in content:
				total_cnt += int(line.split()[1])
			content.seek(0,0)
			for line in content:
				acc_cnt += int(line.split()[1])
				if (acc_cnt / total_cnt >= 0.99):
					maxCLSizes_capped_rll.append(float(line.split()[0]) * 64 / 1024)
					break
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

	missRatios_rll_max = []
	maxCLSizes_rll_max = []
	if (len(cacheSizes_rll) == len(missRatios_rll) and len(missRatios_rll) == len(maxCLSizes_rll)):
		for i in range(len(cacheSizes_rll)):
			if (i == len(cacheSizes_rll) - 1):
				missRatios_rll_max.append(missRatios_rll[i])
				maxCLSizes_rll_max.append(maxCLSizes_rll[i])
			else:
				missRatios_rll_max.append(missRatios_rll[i])
				maxCLSizes_rll_max.append(maxCLSizes_rll[i])
				missRatios_rll_max.append(missRatios_rll[i] - 0.000000000000001)
				maxCLSizes_rll_max.append(maxCLSizes_rll[i+1])
			

	#if (maxCLSizes_rll != []):
	#	maxCLSizes_rll.pop(0)
	#	maxCLSizes_rll.append(maxCLSizes_rll[-1])	

	

	#if ("ludcmp" in f):
		#for index in range(len(cacheSizes_rll)):
		#	print cacheSizes_rll[index], maxCLSizes_rll[index], missRatios_rll[index]
		#for index in range(len(cacheSizes)):
		#	print cacheSizes[index], missRatios[index]

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
	
	while(len(missRatios_opt) > 2):
		if (missRatios_opt[-1] == missRatios_opt[-2]):
			del missRatios_opt[-1]
			del cacheSizes_opt[-1]
		else:
			break		

		


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
	ax.set_title(f.replace("_trace_result.txt",""), fontsize = 10, y = 0.6, x = 0.6)
	l1 = ax.plot(cacheSizes, missRatios, '#5e3c99', linewidth=2.5, label = "LRU")[0]
	l2 = l1
	'''
	if (len(maxCLSizes_rll) == len(missRatios_rll)):
		l2 = ax.plot(maxCLSizes_rll_max, missRatios_rll_max, '#fdb863', linewidth=2, label = "RL-MAX")[0]
	'''
	if (len(maxCLSizes_rll) == len(missRatios_rll)):
		l2 = ax.plot(maxCLSizes_rll, missRatios_rll, "1" ,color = '#fdb863', linewidth=2, label = "RL-MAX")[0]
	l3 = ax.plot(cacheSizes_rll, missRatios_rll, '#b2abd2', linewidth=1.5, label = "RL-AVG")[0]
	l4 = ax.plot(cacheSizes_opt, missRatios_opt, '#e66101', linewidth=1, label = "OPT")[0]
	l5 = l4
	if (len(maxCLSizes_capped_rll) == len(missRatios_rll)):
		l5 = ax.plot(maxCLSizes_capped_rll, missRatios_rll, "2", color = 'black', label = "CAPPED")[0]
	
	if (fig_cnt == 29):
		ax.set_xlabel('Cache Size (KB)')
	if (fig_cnt == 16):
		ax.set_ylabel('Miss Ratio')
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

	if (f.replace("_trace_result.txt","") in yMax.keys()):
		ax.set_ylim(top = yMax[f.replace("_trace_result.txt","")])
	ax.set_ylim(bottom = 0)

	if (fig_cnt == 1):
		fig.legend([l1, l2, l5, l3, l4], ["LRU", "RL-MAX", "CAPPED", "RL-AVG", "OPT"], ncol=5, mode="expand", loc = "upper center")

	fig_cnt += 1

plt.tight_layout(pad=0.4, w_pad=0.4, h_pad=-0.9)
plt.subplots_adjust(left=0.09, right = 0.98, top = 0.95, bottom = 0.07)
plt.show()
#plt.savefig(figPath + "all.pdf")
