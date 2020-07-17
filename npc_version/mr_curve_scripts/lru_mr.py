import argparse
def get_bins(filename):
	bins = {}
	endpts = []
	num_acc=0
	with open(filename,'r') as f:
		lines = f.readlines()
		for i,line in enumerate(lines):
			s = line.split()
			if(len(s)>1):
					if(s[1]=="Total" ):
						if(s[4]=="accesses"):
							num_acc=eval(s[-2])
					if(s[1]=="Bin"):
						endpts.append(eval(s[4]))
						if(s[-2]!="SLQ:"):
							bins[eval(s[2])] = eval(s[-1])
						else:
							bins[eval(s[2])] = eval(s[-3])
		endpts.append(eval(lines[-2].split()[6]))
	return bins,endpts,num_acc


def get_log_iters(maximum):
	num=1
	pwr=0 
	bounds=[]
	while(True):
		if(num*10**pwr > maximum):
			break
		bounds.append(num * (10**pwr))
		num+=1
		if(num==10):
			num=1
			pwr += 1
	return bounds


def get_mrs(bins,endpts,num_acc):

	best={}
	worst={}

	mins={}
	maxs={}

	
	mr = 1
	mrs={}


	s = 0
	for b in bins:
		s+=bins[b]

	print(f"num_reuses: {s}")	
	s2 = 0
	for b in bins:
		#print(bins[b])
		s2+=bins[b]
		#print("\t"+str(s2))
		#mr -= bins[b] / s
		mrs[b]=1-(s2/s)

#	for b,mr in mrs.items():
#		print(f"{b} {mr}")
	
	for i,e in enumerate(endpts):
		if(i>0):

			if(i==len(endpts)-1):
				mins[i] = 0.0
				maxs[i] = 0.0
			else:
				mins[i] = mrs[i-1]
				maxs[i] = mrs[i]
		else:
			mins[i] = mrs[i]
			maxs[i] = mrs[i]
	
	return mins,maxs

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("filename")
	args=parser.parse_args()
	
	bins,endpts,num_acc = get_bins(args.filename)
	print(f"number of accesses: {num_acc}")
	mins,maxs = get_mrs(bins,endpts,num_acc)
	for m in mins:
		print(f"cache_size {endpts[m]} max_mr {mins[m]} min_mr {maxs[m]}")
if __name__=="__main__":
	main()
