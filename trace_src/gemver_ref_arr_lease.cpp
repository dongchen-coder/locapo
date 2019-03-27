
#include "../utility/rt.h"
#include "../utility/data_size.h"

#ifdef ORG
	#define N 1024
#elif defined(TX)
	#define N 1448
#elif defined(FX)
	#define N 2048
#elif defined(EX)
	#define N 2896
#endif

#define A_OFFSET 0
#define u1_OFFSET N * N  
#define v1_OFFSET N * N + N
#define u2_OFFSET N * N + N + N
#define v2_OFFSET N * N + N + N + N
#define W_OFFSET N * N + N + N + N + N 
#define X_OFFSET N * N + N + N + N + N + N
#define Y_OFFSET N * N + N + N + N + N + N + N
#define Z_OFFSET N * N + N + N + N + N + N + N + N

void gemver_trace(double alpha, double beta, double* A, double* u1, double* v1, double* u2, double* v2, double* w, double* x, double* y, double* z)
{
	int i,j;

    for (i = 0; i < N; i++)
    {
        for (j = 0; j < N; j++)
        {
            A[i * N + j] = A[i * N + j] + u1[i] * v1[j] + u2[i] * v2[j];
			trackingLease(A_OFFSET + i * N + j, 0, 0,5);
			trackingLease(u1_OFFSET + i, 1, 1,6);
			trackingLease(v1_OFFSET + j, 2, 1,6102);
			trackingLease(u2_OFFSET + i, 3, 2,6);
			trackingLease(v2_OFFSET + j, 4, 2,6102);
			trackingLease(A_OFFSET + i * N + j, 5, 0,10446850);
       }
    }

    for (i = 0; i < N; i++)
    {
        for (j = 0; j < N; j++)
        {
            x[i] = x[i] + beta * A[j * N + i] * y[j];
			trackingLease(X_OFFSET + i, 6, 3,3);
			trackingLease(A_OFFSET + j * N + i, 7, 0,8342544);
			trackingLease(Y_OFFSET + j, 8, 4,4068);
			trackingLease(X_OFFSET + i, 9, 3,4161537);
        }
    }

    for (i = 0; i < N; i++)
    {
        x[i] = x[i] + z[i];
		trackingLease(X_OFFSET + i, 10, 3,2);
		trackingLease(Z_OFFSET + i, 11, 5,3);
		trackingLease(X_OFFSET + i, 12, 3,4067);
    }

    for (i = 0; i < N; i++)
    {
        for (j = 0; j < N; j++)
        {
            w[i] = w[i] +  alpha * A[i * N + j] * x[j];
			trackingLease(W_OFFSET + i, 13, 6,3);
			trackingLease(A_OFFSET + i * N + j, 14, 0,4);
			trackingLease(X_OFFSET + j, 15, 3,4068);
			trackingLease(W_OFFSET + i, 16, 6,1);
        }
    }
}

int main(int argc, char const *argv[])
{
    double* u1 = (double*)malloc( N * sizeof(double));
    double* v1 = (double*)malloc( N * sizeof(double));
    double* u2 = (double*)malloc( N * sizeof(double));
    double* v2 = (double*)malloc( N * sizeof(double));
    double* A = (double*)malloc( (N*N) * sizeof(double));
    double* y = (double*)malloc( N * sizeof(double));
    double* x = (double*)malloc( N * sizeof(double));
    double* z = (double*)malloc( N * sizeof(double));
    double* w = (double*)malloc( N * sizeof(double));

    for (int i = 0; i < N; ++i)
    {
        u1[i] = i % 256;
        u2[i] = i % 32;
        v1[i] = i % 2;
        v2[i] = i % 512;
        y[i] = i % 4;
        z[i] = i % 64;
        x[i] = 0.0;
        w[i] = 0.0;
    }

    for (int i = 0; i < N*N; ++i)
    {
        A[i] = 0.0;
    }

    double alpha = 1.0;
    double beta = 1.5;

    gemver_trace(alpha, beta, A, u1, v1, u2, v2, w, x, y, z);
dumpMaxNumOfCL();	
    return 0;
}
