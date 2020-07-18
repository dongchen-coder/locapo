#include <iostream>
#include <set>
#include <map>
#include <limits>
using namespace std;

#define CLS 64
#define DS 8

uint64_t refT = 0;

map<uint64_t, uint64_t> lat;

map<uint64_t, double> RI;

// get reuse interval distribution
void rtTmpAccess(uint64_t addr, uint64_t ref_id, uint64_t arr_id) {
	refT++;
	addr = addr * DS / CLS;
	
	// update last access table
	if (lat.find(addr) != lat.end()) {
		uint64_t ri = refT - lat[addr];
		if (RI.find(ri) != RI.end()) {
			RI[ri] += 1;
		} else {
			RI[ri] = 1;
		}
	}
	lat[addr] = refT;
	
	return;
}

// dump RI
void dumpRI() {
	cout << "Total number of accesses " << refT << endl;
	cout << "printing distribution:" << endl;
    uint64_t total_number_of_ri_cnt = 0;
    for (map<uint64_t, double>::iterator ri_it = RI.begin(), ri_eit = RI.end(); ri_it != ri_eit; ++ri_it) {
		total_number_of_ri_cnt += ri_it->second;
    }

    for (map<uint64_t, double>::iterator ri_it = RI.begin(), ri_eit = RI.end(); ri_it != ri_eit; ++ri_it) {
    	cout << "ri: " << ri_it->first << " freq: " << double(ri_it->second) / total_number_of_ri_cnt << endl;
    }
}

// main OSL_ref alg
void OSL_ref(uint64_t CacheSize) {
	
	dumpRI();

	return;
}
