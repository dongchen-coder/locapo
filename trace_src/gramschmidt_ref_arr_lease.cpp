
#include "../utility/rt.h"
#include "../utility/data_size.h"

#include <math.h>

#ifdef ORG
	#define N 1024
	#define M 1024
#elif defined(TX)
#elif defined(FX)
#elif defined(EX)
#endif

#define A_OFFSET 0
#define R_OFFSET N * M
#define Q_OFFSET N * M + N * N

void gramschmidt_trace(double* A, double* R, double* Q) {

	int k, i, j;
	double nrm;

	for (k = 0; k < N; k++) {
		nrm = 0.0;
		for (i = 0; i < M; i++) {
			nrm += A[i * N + k] * A[i * N + k];
			trackingLease(A_OFFSET + i * N + k, 0, 0,1);
			trackingLease(A_OFFSET + i * N + k, 1, 0,3064);
		}
		R[k * N + k] = sqrt(nrm);
		trackingLease(R_OFFSET + k * N + k, 2, 1,2);
		for (i = 0; i < M; i++) {
			Q[i * N + k] = A[i * N + k] / R[k * N + k];
			trackingLease(A_OFFSET + i * N + k, 3, 0,3074);
			trackingLease(R_OFFSET + k * N + k, 4, 1,3);
			trackingLease(Q_OFFSET + i * N + k, 5, 2,3071);
		}
		for (j = k + 1; j < N; j++) {
			R[k * N + j] = 0.0;
			trackingLease(R_OFFSET + k * N + j, 6, 1,3);
			for (i = 0; i < M; i++) {
				R[k * N + j] += Q[i * N + k] * A[i * N + j];
				trackingLease(Q_OFFSET + i * N + k, 7, 2,4096);
				trackingLease(A_OFFSET + i * N + j, 8, 0,4088);
				trackingLease(R_OFFSET + k * N + j, 9, 1,3);
			}
			for (i = 0; i < M; i++) {
        		A[i * N + j] = A[i * N + j] - Q[i * N + k] * R[k * N + j];
				trackingLease(A_OFFSET + i * N + j, 10, 0,3);
				trackingLease(Q_OFFSET + i * N + k, 11, 2,6146);
				trackingLease(R_OFFSET + k * N + j, 12, 1,4);
				trackingLease(A_OFFSET + i * N + j, 13, 0,7287797);
			}
		}
    }
}

int main() {

	double * A = (double *)malloc(N * M * sizeof(double));
	double * R = (double *)malloc(N * N * sizeof(double));
	double * Q = (double *)malloc(M * N * sizeof(double));

	gramschmidt_trace(A, R, Q);
	
dumpMaxNumOfCL();
	return 0;
}
