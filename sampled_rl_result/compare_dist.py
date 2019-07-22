import os

sampled_02_path = './sampled_rl_assignment_0.02/'
sampled_05_path = './sampled_rl_assignment_0.05/'
sampled_10_path = './sampled_rl_assignment_0.10/'

names = ['syr2d']

for name in names:
	content = open(sampled_02_path + name + '_staticSampling_result.txt', 'r')

	total_cnt = 0
	for line in content:
		if ('Ref' in line and 'RI' in line and 'CNT' in line):
			linetmp = line.split()
			ref = int(linetmp[1])
			ri = int(linetmp[3])
			cnt = int(linetmp[5])
			total_cnt += cnt

	content.seek(0)
	for line in content:
		if ('Ref' in line and 'RI' in line and 'CNT' in line):
			linetmp = line.split()
			ref = int(linetmp[1])
			ri = int(linetmp[3])
			cnt = int(linetmp[5])
			print 'Ref', ref, 'RI', ri, 'DIST', float(cnt) / total_cnt
	content.close()
			
