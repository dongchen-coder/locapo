import os

rll_cappedMaxNumOfCLSize_path = "./poly_trace_rll_CLSizes/"
rll_path = "./poly_trace_rll/"
lru_path = "./poly_trace_lru_2/"
files = os.listdir(lru_path)

names = []
sorted_names = []
for f in sorted(files):
	name = f.replace("_trace_result.txt","")
	if (name not in names):
		sorted_names.append(name)
sorted_names += sorted(names)

for name in sorted_names:
	
	f = name + "_trace_result.txt"

	if (".DS_Store" in f):
		continue
	
	cacheSizes_rll = []
	missRatios_rll = []
	if (os.path.exists(rll_path + f.replace("_trace_result.txt","") + "_ref_arr.cpp.o.tr.txt")):
		content = open(rll_path + f.replace("_trace_result.txt","") + "_ref_arr.cpp.o.tr.txt", 'r')
		for line in content:
			if ("Total costs (block)" in line):
				lineList = line.split()
				cacheSizes_rll.append(float(lineList[4]) * 64 / 1024)
			if ("Miss ratio" in line):
				lineList = line.split()
				missRatios_rll.append(float(lineList[2]))
		content.close()

	maxCLSizes_capped_rll = []
	missRatios_capped_rll = []
	for i in range(len(cacheSizes_rll)):
		if (os.path.exists( rll_cappedMaxNumOfCLSize_path + f.replace("_trace_result.txt","") + "_lease_" + str(i) + "_rll_CLSize.txt")):
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
	print name
	print maxCLSizes_capped_rll
