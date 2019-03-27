
#include "../utility/rt.h"
#include "../utility/data_size.h"

#ifdef ORG
	#define N 1024
#elif defined(TX)
#elif defined(FX)
#elif defined(EX)
#endif

#define PATH_OFFSET 0

void floyd_warshall_trace(double* path) {

	int k, i, j;

	for (k = 0; k < N; k++) 
		for(i = 0; i < N; i++)
			for (j = 0; j < N; j++) {
				//path[i * N + j] = path[i * N + j] < path[i * N + k] + path[k * N + j] ? path[i * N + j] : path[i * N + k] + path[k * N + j];
				trackingLease(PATH_OFFSET + i * N + j, 0, 0,5);
				trackingLease(PATH_OFFSET + i * N + k, 1, 0,2);
				trackingLease(PATH_OFFSET + k * N + j, 2, 0,2);
				if (path[i * N + j] < path[i * N + k] + path[k * N + j]) {
					path[i * N + j] = path[i * N + j];
					trackingLease(PATH_OFFSET + i * N + j, 3, 0,0);
					trackingLease(PATH_OFFSET + i * N + j, 4, 0,0);
				} else {
					path[i * N + j] = path[i * N + k] + path[k * N + j];
					trackingLease(PATH_OFFSET + i * N + k, 5, 0,6279173);
					trackingLease(PATH_OFFSET + k * N + j, 6, 0,6279122);
					trackingLease(PATH_OFFSET + i * N + j, 7, 0,6285267);
				}
			}
}

int main() {

	double* path = (double *)malloc(N * N * sizeof(double));

	floyd_warshall_trace(path);

dumpMaxNumOfCL();
	return 0;
}
