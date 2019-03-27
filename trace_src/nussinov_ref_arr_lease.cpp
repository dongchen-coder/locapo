
#include "../utility/rt.h"
#include "../utility/data_size.h"

#include <math.h>

#ifdef ORG
	#define N 1024
#elif defined(TX)
#elif defined(FX)
#elif defined(EX)
#endif

#define match(b1, b2) (((b1)+(b2)) == 3 ? 1 : 0)
#define max_score(s1, s2) ((s1 >= s2) ? s1 : s2)


#define TABLE_OFFSET 0
#define SEQ_OFFSET N * N

void nussinov_trace(double* table, double* seq) {

	int i, j, k;

	for (i = N - 1; i >= 0; i--) {
		for (j=i+1; j < N; j++) {
			if (j-1>=0) {
				table[i * N + j] = max_score(table[i * N + j], table[i * N + j-1]);
				trackingLease(TABLE_OFFSET + i * N + j, 0, 0,3);
				trackingLease(TABLE_OFFSET + i * N + j-1, 1, 0,2592326);
				if (table[i * N + j] > table[i * N + j-1])
					trackingLease(TABLE_OFFSET + i * N + j, 2, 0,1);
				else
					trackingLease(TABLE_OFFSET + i * N + j-1, 3, 0,2017345);
				trackingLease(TABLE_OFFSET + i * N + j, 4, 0,1);
			}
			if (i+1 < N) {
				table[i * N +j] = max_score(table[i * N + j], table[(i+1) * N + j]);
				trackingLease(TABLE_OFFSET + i * N + j, 5, 0,2);
				trackingLease(TABLE_OFFSET + (i+1) * N + j, 6, 0,5089);
				if (table[i * N + j] >= table[(i+1) * N + j])
					trackingLease(TABLE_OFFSET + i * N + j, 7, 0,1);
				else
					trackingLease(TABLE_OFFSET + i * N + j, 8, 0,0);
				trackingLease(TABLE_OFFSET + i * N + j, 9, 0,1);
			}
			if (j-1>=0 && i+1 < N) {
				/* don't allow adjacent elements to bond */
				if (i<j-1) {
					table[i * N + j] = max_score(table[i * N + j], table[(i+1) * N + j-1]+match(seq[i], seq[j]));
					trackingLease(TABLE_OFFSET + i * N + j, 10, 0,4);
					trackingLease(TABLE_OFFSET + (i+1) * N + j-1, 11, 0,2622823);
					trackingLease(SEQ_OFFSET + i, 12, 1,5121);
					trackingLease(SEQ_OFFSET + j, 13, 1,2622592);
					if (table[i * N + j] >= table[(i+1) * N + j-1]+match(seq[i], seq[j])) {
						trackingLease(TABLE_OFFSET + i * N + j, 14, 0,1);
					} else {
						trackingLease(TABLE_OFFSET + (i+1) * N + j-1, 15, 0,0);
                    	trackingLease(SEQ_OFFSET + i, 16, 1,0);
                    	trackingLease(SEQ_OFFSET + j, 17, 1,0);
					}
					trackingLease(TABLE_OFFSET + i * N + j, 18, 0,1);
				} else {
					table[i * N + j] = max_score(table[i * N + j], table[(i+1) * N + j-1]);
					trackingLease(TABLE_OFFSET + i * N + j, 19, 0,2);
					trackingLease(TABLE_OFFSET + (i+1) * N + j-1, 20, 0,31);
					if (table[i * N + j] >= table[(i+1) * N + j-1]) {
						trackingLease(TABLE_OFFSET + i * N + j, 21, 0,1);
					} else {
						trackingLease(TABLE_OFFSET + i * N + j, 22, 0,0);
					}
					trackingLease(TABLE_OFFSET + i * N + j, 23, 0,6);
				}
			}
			for (k=i+1; k<j; k++) {
				table[i * N + j] = max_score(table[i * N + j], table[i * N + k] + table[(k+1) * N + j]);
				trackingLease(TABLE_OFFSET + i * N + j, 24, 0,3);
				trackingLease(TABLE_OFFSET + i * N + k, 25, 0,2541701);
				trackingLease(TABLE_OFFSET + (k+1) * N + j, 26, 0,2621441);
				if (table[i * N + j] >= table[i * N + k] + table[(k+1) * N + j]) {
					trackingLease(TABLE_OFFSET + i * N + j, 27, 0,1);
				} else {
					trackingLease(TABLE_OFFSET + i * N + k, 28, 0,0);
                	trackingLease(TABLE_OFFSET + (k+1) * N + j, 29, 0,0);
				}
				trackingLease(TABLE_OFFSET + i * N + j, 30, 0,2582155);
			}
		}
	}
}

int main() {

	double* table = (double *)malloc(N * N * sizeof(double));
	double* seq = (double *)malloc(N * sizeof(double));

	for (int i = 0; i < N; i++) {
		for (int j = 0; j < N; j++) {
			table[i * N + j] = (i * N + j) % 128;
		}
		seq[i] = i % 64;
	}

	nussinov_trace(table, seq);

dumpMaxNumOfCL();
	return 0;
}
