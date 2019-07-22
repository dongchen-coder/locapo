import os

ri_path = './full_ri_dis_for_sampled_rl/'
sampled_rl_assignment_path = './sampled_rl_assignment_0.10/'
sampled_rl_mrc_path = './sampled_rl_mrc_0.10/'

def readAccessCnt(src_path, name):
	content = open(src_path + name + '_ref_arr_trace_result.txt', 'r')
	ri = {}
	refAccessCnt = {}
	total_accesses = 0
	for line in content:
		linetmp = line.split()
		if ('Ref' in line and 'RI' in line and 'CNT' in line):
			ref = int(linetmp[1])
			ri_tmp = int(linetmp[3])
			cnt = int(linetmp[5])
			if (ref in ri.keys()):
				ri[ref][ri_tmp] = cnt
			else:
				ri[ref] = {}
				ri[ref][ri_tmp] = cnt
		if ('Total number of accesses' in line):
			total_accesses = int(linetmp[4])
		if ('ACCESSCNT' in line):
			ref = int(linetmp[1])
			accessCnt = int(linetmp[3])
			if (ref in refAccessCnt.keys()):
				print "Error printing access cnt"
			else:
				refAccessCnt[ref] = accessCnt

	content.close()
	return ri, refAccessCnt, total_accesses


def calRL(src_path, result_path, name, ri, refAccessCnt, total_accesses):
	content = open(src_path + name + '_staticSampling_result.txt', 'r')
	result_file = open(result_path + name + '_mrc.txt', 'w')

	Lease = {}
	total_cost = 0.0
	total_hit = 0.0
	for line in content:
		if ('Assign lease' not in line):
			continue

		linetmp = line.split()
		ref_to_assign = int(linetmp[5])
		lease_to_assign = int(linetmp[2])

		# if ref assigned does not have reuses
		if (ref_to_assign not in ri.keys()):
			# if ref assigned does not have accesses
			if (ref_to_assign not in refAccessCnt.keys()):
				refAccessCnt[ref_to_assign] = 0
			# if ref assigned has an old lease
			if (ref_to_assign in Lease.keys()):
				total_cost += (lease_to_assign - Lease[ref_to_assign]) * refAccessCnt[ref_to_assign]
			else:
				total_cost += lease_to_assign * refAccessCnt[ref_to_assign]
			print "Warning in SPS RI sampling: no RI in ref ", ref_to_assign
			Lease[ref_to_assign] = lease_to_assign
			result_file.write("cache size " + str(float(total_cost) / total_accesses) + " miss ratio " + str(1 - float(total_hit) / total_accesses) + "\n")
			continue
		
		# if ref assigned has reuses
		for ri_tmp in ri[ref_to_assign].keys():
			# if ref assigned has an old lease
			if (ref_to_assign in Lease.keys()):
				if (ri_tmp <= lease_to_assign and ri_tmp > Lease[ref_to_assign]):
					total_hit += ri[ref_to_assign][ri_tmp]
					total_cost += ri[ref_to_assign][ri_tmp] * (ri_tmp - Lease[ref_to_assign])
				elif (ri_tmp > lease_to_assign):
					total_cost += ri[ref_to_assign][ri_tmp] * (lease_to_assign - Lease[ref_to_assign])
			# if ref assgined does not have an old lease
			else:
				if (ri_tmp <= lease_to_assign):
					total_hit += ri[ref_to_assign][ri_tmp]
					total_cost += ri[ref_to_assign][ri_tmp] * ri_tmp
				else:
					total_cost += ri[ref_to_assign][ri_tmp] * lease_to_assign
		Lease[ref_to_assign] = lease_to_assign

		result_file.write("cache size " + str(float(total_cost) / total_accesses) + " miss ratio " + str(1 - float(total_hit) / total_accesses) + "\n")

	content.close()
	result_file.close()
	return




names = ['2mm', 'deriche', 'gramschmidt', 'seidel_2d', '3mm', 'doitgen', 'heat_3d', 'symm', 'adi', 'durbin', 'jacobi_1d', 'syr2d', 'atax', 'fdtd_2d', 'jacobi_2d', 'syrk', 'bicg', 'floyd_warshall', 'lu', 'trisolv', 'cholesky', 'gemm', 'ludcmp', 'trmm', 'correlation', 'gemver', 'mvt', 'covariance', 'gesummv', 'nussinov']

for name in names:
	for rate in ['0.10', '0.05', '0.02']:
		print "Process ", name
	
		sampled_rl_assignment_path = './sampled_rl_assignment_' + rate +'/'
		sampled_rl_mrc_path = './sampled_rl_mrc_' + rate + '/'	

		ri, refAccessCnt, total_accesses = readAccessCnt(ri_path, name)
		calRL(sampled_rl_assignment_path, sampled_rl_mrc_path, name, ri, refAccessCnt, total_accesses)
'''
ri, refAccessCnt, total_accesses = readAccessCnt(ri_path, '2mm')
calRL('./', './', '2mm', ri, refAccessCnt, total_accesses)
'''
