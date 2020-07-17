from tqdm import tqdm
import argparse
#return power of 2
LEASE = 0
def get_log_bin(num:int): 
	pwr = 0
	while(num >1):
		num>>=1
		pwr+=1
	return 2 << pwr

def generate_dist(filename,mode="mr"):
	dist={}
	rimax=0
	trace_len=0 #lies
	num_acc = 0
	unique_refs=[]
	unique_ris=0
	with open(filename,'r') as f:
		lines = f.readlines()
		for line in lines[2:]:
			ws=line.split()
			if(ws[2]=="RI"):
				if(ws[4]=="CNT"):
					ri = eval(ws[3])
					if(mode=="ri"):
						if(eval(ws[1]) not in unique_refs):
							unique_refs.append(eval(ws[1]))
						else:
							unique_ris+=1
					if ri > (2 << 20) :
						ri = get_log_bin(ri)
					if(ri not in dist):
						dist[ri]=0
					dist[ri]+=eval(ws[5])
					num_acc+=eval(ws[5])
			if(ri>rimax): rimax=ri
	for d in dist:
		trace_len+=dist[d]
	for d in dist:
		dist[d]/=trace_len
	return dist,rimax,len(unique_refs),unique_ris

def print_dist(dist,unique_refs,unique_ris):
	print(f"num_unique_refs: {unique_refs} num_unique_ris_raw: {unique_ris} num_unique_ri_bins: {len(dist)}")
	print("printing distribution:")

	for d in dist:
		print(f"ri: {d} freq: {dist[d]}")
		
def get_cache_size(dist,lease):
	s = 0
	for x,freq in dist.items():
		if(x < lease):
			s += (lease-x)*freq
	return lease - s 

def get_lease(dist,cachesize,rimax):
	l=0 
	pwr = 8
	while True:
		candidate = l+10**pwr
		if get_cache_size(dist,candidate) > cachesize:
			pwr -=1 
			if(pwr < 0):
				return l
		else:
			l = candidate
			if(l > rimax):
				return rimax
	
def get_mr(dist,lease):
	mr=0
	for ri,freq in dist.items():
		if ri > lease:
			mr+=freq
	return mr 

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

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("mode",help="mr: compute miss ratio curve. ri: print ri distribution")
	parser.add_argument("filename",help="input file")
	args = parser.parse_args()	

	if(args.mode == "mr"):
		dist,rimax,_,_=generate_dist(args.filename)
		print("printing miss ratio curve:")
		for cache_size in get_log_iters(300000):
			lease = get_lease(dist,cache_size,rimax) 
			mr = get_mr(dist,lease)
			print(f"cache_size {cache_size} miss_ratio {mr} lease {lease}")
	elif(args.mode == "ri"):
		dist,_,unique_refs,unique_ris=generate_dist(args.filename,args.mode)
		print_dist(dist,unique_refs,unique_ris)

if __name__=="__main__":
	main()


