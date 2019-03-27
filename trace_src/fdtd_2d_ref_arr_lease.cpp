
#include "../utility/rt.h"
#include "../utility/data_size.h"

#ifdef ORG
	#define _PB_TMAX 10
	#define _PB_NY 1024
	#define _PB_NX 1024
#elif defined(TX)
#elif defined(FX)
#elif defined(EX)
#endif

#define FICT_OFFSET 0
#define EY_OFFSET _PB_TMAX
#define EX_OFFSET _PB_TMAX + _PB_NX * _PB_NY
#define HZ_OFFSET _PB_TMAX + _PB_NX * _PB_NY + _PB_NX * _PB_NY


void fdtd_2d_trace(double* _fict_, double* ey, double* ex, double* hz) {

	int t, i, j;

	for(t = 0; t < _PB_TMAX; t++) {
		for (j = 0; j < _PB_NY; j++) {
			ey[0 * _PB_NY + j] = _fict_[t];
			trackingLease(FICT_OFFSET + t, 0, 0,14659592);
			trackingLease(EY_OFFSET + 0 * _PB_NY + j, 1, 1,8382457);
		}

		for (i = 1; i < _PB_NX; i++)
			for (j = 0; j < _PB_NY; j++) {
				ey[i * _PB_NY + j] = ey[i * _PB_NY + j] - 0.5 * (hz[i * _PB_NY + j] - hz[(i-1) * _PB_NY + j]);
				trackingLease(EY_OFFSET + i * _PB_NY + j, 2, 1,3);
				trackingLease(HZ_OFFSET + i * _PB_NY + j, 3, 2,4190180);
				trackingLease(HZ_OFFSET + (i-1) * _PB_NY + j, 4, 2,4190187);
				trackingLease(EY_OFFSET + i * _PB_NY + j, 5, 1,10453004);
			}

		for (i = 0; i < _PB_NX; i++)
			for (j = 1; j < _PB_NY; j++) {
				ex[i * _PB_NY + j] = ex[i * _PB_NY + j] - 0.5 * (hz[i * _PB_NY + j]-hz[i * _PB_NY + j - 1]);
				trackingLease(EX_OFFSET + i * _PB_NY + j, 6, 3,3);
				trackingLease(HZ_OFFSET + i * _PB_NY + j, 7, 2,4);
				trackingLease(HZ_OFFSET + i * _PB_NY + j - 1, 8, 2,10471397);
				trackingLease(EX_OFFSET + i * _PB_NY + j, 9, 3,14661607);
			}

		for (i = 0; i < _PB_NX - 1; i++)
			for (j = 0; j < _PB_NY - 1; j++) {
				hz[i * _PB_NY + j] = hz[i * _PB_NY + j] - 0.7 * (ex[i * _PB_NY + j + 1] - ex[i * _PB_NY + j] + ey[(i+1) * _PB_NY + j] - ey[i * _PB_NY + j]);
    			trackingLease(HZ_OFFSET + i * _PB_NY + j, 10, 2,5);
				trackingLease(EX_OFFSET + i * _PB_NY + j + 1, 11, 3,6);
				trackingLease(EX_OFFSET + i * _PB_NY + j, 12, 3,10471370);
				trackingLease(EY_OFFSET + (i+1) * _PB_NY + j, 13, 1,4194241);
				trackingLease(EY_OFFSET + i * _PB_NY + j, 14, 1,6279141);
				trackingLease(HZ_OFFSET + i * _PB_NY + j, 15, 2,6281189);
			}
	}

}

int main() {

	double* _fict_ = (double *)malloc(_PB_TMAX * sizeof(double));
	double* ey = (double *)malloc(_PB_NX * _PB_NY * sizeof(double));
	double* ex = (double *)malloc(_PB_NX * _PB_NY * sizeof(double));
	double* hz = (double *)malloc(_PB_NX * _PB_NY * sizeof(double));	

	fdtd_2d_trace(_fict_, ey, ex, hz);

dumpMaxNumOfCL();
	return 0;
}