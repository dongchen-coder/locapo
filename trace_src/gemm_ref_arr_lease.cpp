
#include "../utility/rt.h"
#include "../utility/data_size.h"


#ifdef ORG
	#define NI 256
	#define NJ 256
	#define NK 256
#elif defined(TX)
	#define NI 256
	#define NJ 256
	#define NK 512
#elif defined(FX)
	#define NI 256
	#define NJ 512
	#define NK 512
#elif defined(EX)
	#define NI 512
	#define NJ 512
	#define NK 512
#endif

#define A_OFFSET 0
#define B_OFFSET NI * NK
#define C_OFFSET NI * NK + NK * NJ

void gemm_trace(double alpha, double beta, double* A, double* B, double* C) {
    int i,j,k;
    
    for (i = 0; i < NI; i++)
    {
        for (j = 0; j < NJ; j++)
        {
            C[i * NJ + j] *= beta;
			trackingLease(C_OFFSET + i * NJ + j, 0, 0,1);
			trackingLease(C_OFFSET + i * NJ + j, 1, 0,1);

            for (k = 0; k < NK; k++)
            {
                C[i * NJ + j] += alpha * A[i * NK + k] * B[k * NJ + j];
				trackingLease(C_OFFSET + i * NJ + j, 2, 0,3);
				trackingLease(A_OFFSET + i * NK + k, 3, 1,998);
				trackingLease(B_OFFSET + k * NJ + j, 4, 2,255474);
				trackingLease(C_OFFSET + i * NJ + j, 5, 0,1);
            }
        }
    }
    return;
}

int main()
{
    double* A = (double*)malloc(NI * NK * sizeof(double));
    double* B = (double*)malloc(NK * NJ * sizeof(double));
    double* C = (double*)malloc(NI * NJ * sizeof(double));

    for (int i = 0; i < NI*NK; ++i)
    {
        A[i] = i % 256;
    }

    for (int i = 0; i < NK * NJ; ++i)
    {
        B[i] = i % 48;
    }

    double alpha = 1.0;
    double beta = 1.5;

    gemm_trace(alpha, beta, A, B, C);
dumpMaxNumOfCL();
    return 0;
}
