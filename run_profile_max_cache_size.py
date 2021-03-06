import os
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

rll_path = "./poly_trace_rll/"
trace_src_path = "./trace_src/"
trace_with_lease_src_path = "./trace_src/trace_with_lease_src/"
#result_path = "./poly_trace_rll_maxCLSize/"
result_path = "./poly_trace_rll_CLSizes/"

assigned_id_list_all = {}
assigned_lease_list_all = {}

files = os.listdir(rll_path)

for f in files:
	name = f.replace("_ref_arr.cpp.o.tr.txt","")
	content = open(rll_path+f, 'r')
	assigned_id_list = []
	assigned_lease_list = []
	for line in content:
		if ("Reference id is" in line):
			assigned_id_list.append(int(line.split()[3]))
		if ("Lease assigned is" in line):
			assigned_lease_list.append(int(line.split()[3]))
	content.close()

	assigned_id_list_all[name] = assigned_id_list
	assigned_lease_list_all[name] = assigned_lease_list


for index in range(len(assigned_id_list_all["ludcmp"])):
	print assigned_id_list_all["ludcmp"][index], assigned_lease_list_all["ludcmp"][index]

exit()

files = os.listdir(trace_src_path)

for f in files:
	if ("_ref_arr.cpp" not in f):
		continue
	#if (not(("symm" in f) or ("jacobi_2d" in f) or ("ludcmp" in f) or ("jacobi_1d" in f) or ("lu" in f))):
	#	continue
	if (("correlation" in f) or ("gramschmidt" in f)):
		continue
	if (not("2mm" in f)):
		continue

	name = f.replace("_ref_arr.cpp","")
	
	codes = open(trace_src_path + f, "r")

	current_lease = {}
	if (name not in assigned_id_list_all.keys()):
		codes.close()
		continue		

	for index in range(len(assigned_id_list_all[name])):
		current_lease[assigned_id_list_all[name][index]] = assigned_lease_list_all[name][index]
		
		codes.seek(0)
		new_codes = open(trace_with_lease_src_path + f.replace(".cpp","_lease_" + str(index) + ".cpp"), 'w')  
		for line in codes:
			if ("rtTmpAccess" in line):
				lineList = line.replace("rtTmpAccess", "trackingLease").split(",")
				ref_id = int(lineList[1])
				replace_line = ""
				replace_line += (lineList[0] + ",")
				replace_line += (lineList[1] + ",")
				if (ref_id in current_lease.keys()):
					replace_line += (lineList[2].replace(");", ","+str(current_lease[ref_id])+");"))
				else:
					replace_line += (lineList[2].replace(");", ",0);"))
				new_codes.write(replace_line)
			elif ("dumpRtTmp" in line):
				new_codes.write("dumpMaxNumOfCL();")
			elif ("RTtoMR_AET" in line or "dumpMR" in line):
				continue
			elif ("../utility/rt.h" in line):
                                replace_line = "#include \"../../utility/rt.h\"\n"
                                new_codes.write(replace_line)
                        elif ("../utility/data_size.h" in line):
                                replace_line = "#include \"../../utility/data_size.h\"\n"
                                new_codes.write(replace_line)
                        else:
				new_codes.write(line)

		new_codes.close()
		
		print name, index
		os.system("g++ -O3 " + trace_with_lease_src_path + f.replace(".cpp","_lease_" + str(index) + ".cpp") + " -o ./bin/" + name + "_lease_" + str(index))
		#os.system("./bin/" + name + " >> " + result_path + name + "_rll_maxCLSize.txt" )
	
	codes.close()


