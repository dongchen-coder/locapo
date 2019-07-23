import os
import matplotlib.pyplot as plt

def calDist(path, name, traced):
	suffix = ''
	if (traced == True):
		suffix = '_ref_arr_trace_result.txt'
	else:
		suffix = '_staticSampling_result.txt'
	
	content = open(path + name + suffix, 'r')
	total_cnt = 0
	for line in content:
		if ('Ref' in line and 'RI' in line and 'CNT' in line):
			linetmp = line.split()
			ref = int(linetmp[1])
			ri = int(linetmp[3])
			cnt = int(linetmp[5])
			total_cnt += cnt
	content.seek(0)
	ridist = {}
	for line in content:
		if ('Ref' in line and 'RI' in line and 'CNT' in line):
			linetmp = line.split()
			ref = int(linetmp[1])
			ri = int(linetmp[3])
			cnt = int(linetmp[5])
			#print 'Ref', ref, 'RI', ri, 'DIST', float(cnt) / total_cnt
			
			if (ref in ridist.keys()):
				ridist[ref][ri] = float(cnt) / total_cnt
			else:
				ridist[ref] = {}
				ridist[ref][ri] = float(cnt) / total_cnt
	content.close()
	return ridist

sampled_02_path = './sampled_rl_assignment_0.02/'
sampled_05_path = './sampled_rl_assignment_0.05/'
sampled_10_path = './sampled_rl_assignment_0.10/'

full_traced_path = './full_ri_dis_for_sampled_rl/'
full_traced_visualized_path = './ri_dis_for_sampled_rl_visualized/'


#names = ['syr2d']
names = ['2mm', 'deriche', 'gramschmidt', 'seidel_2d', '3mm', 'doitgen', 'heat_3d', 'symm', 'adi', 'durbin', 'jacobi_1d', 'syr2d', 'atax', 'fdtd_2d', 'jacobi_2d', 'syrk', 'bicg', 'floyd_warshall', 'lu', 'trisolv', 'cholesky', 'gemm', 'ludcmp', 'trmm', 'correlation', 'gemver', 'mvt', 'covariance', 'gesummv', 'nussinov']

for name in names:
	
	ridist = calDist(full_traced_path, name, True)
	ridist_sampled_02 = calDist(sampled_02_path, name, False)
	ridist_sampled_05 = calDist(sampled_05_path, name, False)
	ridist_sampled_10 = calDist(sampled_10_path, name, False)

	for ref in ridist:
		'''
		plt.plot(range(len(ridist[ref])), list(ridist[ref].values()), color = 'y', label = 'Traced RI')
		plt.plot(range(len(ridist[ref])), list(ridist[ref].values()), 'yo')
		if (ref in ridist_sampled_02.keys()):
			plt.plot(range(len(ridist_sampled_02[ref])), list(ridist_sampled_02[ref].values()), color = 'b', label = 'Sampled 2%')
			plt.plot(range(len(ridist_sampled_02[ref])), list(ridist_sampled_02[ref].values()), 'bo')
		else:
			plt.plot([],[],color = 'b')
			plt.plot([],[],color = 'bo')
		if (ref in ridist_sampled_05.keys()):
			plt.plot(range(len(ridist_sampled_05[ref])), list(ridist_sampled_05[ref].values()), color = 'c', label = 'Sampled 5%')
			plt.plot(range(len(ridist_sampled_05[ref])), list(ridist_sampled_05[ref].values()), 'co')
		else:
			plt.plot([],[],color = 'c')
			plt.plot([],[],color = 'co')
		if (ref in ridist_sampled_10.keys()):
			plt.plot(range(len(ridist_sampled_10[ref])), list(ridist_sampled_10[ref].values()), color = 'r', label = 'Sampled 10%')
			plt.plot(range(len(ridist_sampled_10[ref])), list(ridist_sampled_10[ref].values()), 'ro')
		else:
			plt.plot([],[],color = 'c')
			plt.plot([],[],color = 'co')
		'''
		ris = []
		dists = []
		for key in sorted(ridist[ref].keys()):
			ris.append(key)
			dists.append(ridist[ref][key])
		plt.plot(ris, dists, color = 'y', label = 'Traced RI', alpha=0.7, linewidth = 2)
		plt.plot(ris, dists, 'yo', alpha=0.7 , linewidth = 2)
		
		ris_02 = []
		dists_02 = []
		if (ref in ridist_sampled_02.keys()):
			for key in sorted(ridist_sampled_02[ref].keys()):
				ris_02.append(key)
				dists_02.append(ridist_sampled_02[ref][key])
		plt.plot(ris_02, dists_02, color = 'b', label = 'Sampled 2%', alpha=0.7, linewidth = 1.5)
		plt.plot(ris_02, dists_02, 'bo', alpha=0.7, linewidth = 2)
				
		ris_05 = []
		dists_05 = []
		if (ref in ridist_sampled_05.keys()):
			for key in sorted(ridist_sampled_05[ref].keys()):
				ris_05.append(key)
				dists_05.append(ridist_sampled_05[ref][key])
		plt.plot(ris_05, dists_05, color = 'c', label = 'Sampled 5%', alpha=0.7, linewidth = 1)
		plt.plot(ris_05, dists_05, 'co', alpha=0.7, linewidth = 2)
		
		ris_10 = []
		dists_10 = []
		if (ref in ridist_sampled_10.keys()):
			for key in sorted(ridist_sampled_10[ref].keys()):
				ris_10.append(key)
				dists_10.append(ridist_sampled_10[ref][key])
		plt.plot(ris_10, dists_10, color = 'r', label = 'Sampled 10%', alpha=0.7, linewidth = 0.5)
		plt.plot(ris_10, dists_10, 'ro', alpha=0.7, linewidth = 2)


		plt.title(name + "_Ref_" + str(ref) + ":  #RI_" + str(len(dists)) + "---#10%_" + str(len(dists_10)) + "---#5%_" + str(len(dists_05)) + "---#2%_" + str(len(dists_02)))
		plt.legend()
		#plt.show()
		#break		
		plt.savefig(full_traced_visualized_path + name + "_ref_" + str(ref) + '.pdf')
		plt.clf()
	#break
	

