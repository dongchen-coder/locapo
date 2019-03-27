
#include "../utility/rt.h"
#include "../utility/data_size.h"

#ifdef ORG
	#define NX 1024
	#define NY 1024
#elif defined(TX)
	#define NX 1024
	#define NY 2048
#elif defined(FX)
	#define NX 1024
	#define NY 4096
#elif defined(EX)
	#define NX 1024
	#define NY 8192
#endif

#define A_OFFSET 0
#define X_OFFSET NX * NY
#define Y_OFFSET NX * NY + NY
#define TMP_OFFSET NX * NY + NY + NY


void atax_cpu_trace(double* A, double* x, double* y, double* tmp, unsigned int dim_size_x, unsigned int dim_size_y) {
    
	int i,j;

    for (i= 0; i < NY; i++)
    {
        y[i] = 0;
    	trackingLease(Y_OFFSET + i, 0, 0,8162);
	}

    for (i = 0; i < NX; i++)
    {
            tmp[i] = 0;
			trackingLease(TMP_OFFSET + i, 1, 1,1);

            for (j = 0; j < NY; j++)
            {
                tmp[i] = tmp[i] + A[i * NY + j] * x[j];
            	trackingLease(TMP_OFFSET + i, 2, 1,3);
				trackingLease(A_OFFSET + i * NY + j, 3, 2,4068);
				trackingLease(X_OFFSET + j, 4, 3,8165);
				trackingLease(TMP_OFFSET + i, 5, 1,3);
			}

            for (j = 0; j < NY; j++)
            {
                y[j] = y[j] + A[i * NY + j] * tmp[i];
            	trackingLease(Y_OFFSET + j, 6, 0,3);
				trackingLease(A_OFFSET + i * NY + j, 7, 2,4);
				trackingLease(TMP_OFFSET + i, 8, 1,4);
				trackingLease(Y_OFFSET + j, 9, 0,8162);
			}
    }


	return;
}



int main() {

    double* A = (double*)malloc( (NX * NY) * sizeof(double) );
    double* x = (double*)malloc( NX * sizeof(double) );
    double* y = (double*)malloc( NY * sizeof(double) );
    double* tmp = (double*)malloc( NX * sizeof(double) );

    for (int i = 0; i < (NX * NY); i++) {
        A[i] = i % 256;
    }

    for (int i = 0; i < NX; i++) {
        x[i] = i % 256;
    }

    atax_cpu_trace(A, x, y, tmp, NX, NY);
dumpMaxNumOfCL();
    return 0;
}
