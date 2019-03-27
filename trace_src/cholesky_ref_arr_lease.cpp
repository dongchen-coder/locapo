
#include "../utility/rt.h"
#include "../utility/data_size.h"
#include <math.h>

#ifdef ORG
	#define N 1024
#elif defined (TX)
#elif defined (FX)
#elif defined (EX)
#endif

#define A_OFFSET 0

void cholesky_trace(double* A) {

	int i, j, k;

	for (i = 0; i < N; i++) {
		for (j = 0; j < i; j++) {
			for (k = 0; k < j; k++) {
				A[i * N + j] -= A[i * N + k] * A[j * N + k];
				trackingLease(A_OFFSET + i * N + k, 0, 0,4059);
				trackingLease(A_OFFSET + j * N + k, 1, 0,2094052);
				trackingLease(A_OFFSET + i * N + j, 2, 0,1);
				trackingLease(A_OFFSET + i * N + j, 3, 0,3);
			}
			A[i * N + j] /= A[j * N + j];
			trackingLease(A_OFFSET + j * N + j, 4, 0,2094080);
			trackingLease(A_OFFSET + i * N + j, 5, 0,1);
			trackingLease(A_OFFSET + i * N + j, 6, 0,4033);
		}
		for (k = 0; k < i; k++) {
			A[i * N + i] -= A[i * N + k] * A[i * N + k];
			trackingLease(A_OFFSET + i * N + k, 7, 0,1);
			trackingLease(A_OFFSET + i * N + k, 8, 0,2094052);
			trackingLease(A_OFFSET + i * N + i, 9, 0,1);
			trackingLease(A_OFFSET + i * N + i, 10, 0,3);
		}
		A[i * N + i] = sqrt(A[i * N + i]);
		trackingLease(A_OFFSET + i * N + i, 11, 0,1);
		trackingLease(A_OFFSET + i * N + i, 12, 0,2094056);
	}
}

int main() {

	double * A = (double *) malloc(N * N * sizeof(double));
	
	cholesky_trace(A);
	
dumpMaxNumOfCL();
	return 0;
}

