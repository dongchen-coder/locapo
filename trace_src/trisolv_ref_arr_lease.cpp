
#include "../utility/rt.h"
#include "../utility/data_size.h"

#ifdef ORG
	#define N 1024
#elif defined(TX)
#elif defined(FX)
#elif defined(EX)
#endif

#define X_OFFSET 0
#define B_OFFSET N
#define L_OFFSET N + N

void trisolv_trace(double* x, double* b, double* L) {

	int i, j;

	for (i = 0; i < N; i++) {
		x[i] = b[i];
		trackingLease(X_OFFSET + i, 0, 0,4);
		trackingLease(B_OFFSET + i, 1, 1,4090);
		for (j = 0; j <i; j++) {
			x[i] -= L[i * N + j] * x[j];
			trackingLease(L_OFFSET + i * N + j, 2, 2,5);
			trackingLease(X_OFFSET + j, 3, 0,4066);
			trackingLease(X_OFFSET + i, 4, 0,1);
			trackingLease(X_OFFSET + i, 5, 0,3);
		}
		x[i] = x[i] / L[i * N + i];
		trackingLease(X_OFFSET + i, 6, 0,2);
		trackingLease(L_OFFSET + i * N + i, 7, 2,0);
		trackingLease(X_OFFSET + i, 8, 0,1);
		trackingLease(X_OFFSET + i, 9, 0,4036);
	}

}

int main() {

	double* x = (double *)malloc(N * sizeof(double));
	double* b = (double *)malloc(N * sizeof(double));
	double* L = (double *)malloc(N * N * sizeof(double));

	trisolv_trace(x, b, L);

dumpMaxNumOfCL();
	return 0;
}

