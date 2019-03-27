
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
#define X1_OFFSET N * N 
#define X2_OFFSET N * N + N
#define Y1_OFFSET N * N + N + N
#define Y2_OFFSET N * N + N + N + N

void runMvt_trace( double* a, double* x1, double* x2, double* y1, double* y2)
{
    int i, j;
    
    for (i=0; i< N; i++)
    {
        for (j=0; j < N; j++)
        {
            //x1[i] = x1[i] + a[i][j] * y1[j];
            x1[i] = x1[i] + a[i * N + j] * y1[j];
		
			trackingLease(X1_OFFSET + i, 0, 0,3);
			trackingLease(A_OFFSET + i * N + j, 1, 1,8351748);
			trackingLease(Y1_OFFSET + j, 2, 2,4068);
			trackingLease(X1_OFFSET + i, 3, 0,1);

        }
    }
    
    for (i=0; i < N; i++)
    {
        for (j=0; j< N; j++)
        {
            //x2[i] = x2[i] + a[j][i] * y2[j];
            x2[i] = x2[i] + a[j * N + i] * y2[j];

			trackingLease(X2_OFFSET + i, 4, 3,3);
			trackingLease(A_OFFSET + j * N + i, 5, 1,4096);
			trackingLease(Y2_OFFSET + j, 6, 4,4068);
			trackingLease(X2_OFFSET + i, 7, 3,1);

        }
    }
    return;
}

int main(int argc, char const *argv[])
{
    double* a = (double*)malloc( (N*N) * sizeof(double));
    double* y1 = (double*)malloc( N * sizeof(double));
    double* x1 = (double*)malloc( N * sizeof(double));
    double* y2 = (double*)malloc( N * sizeof(double));
    double* x2 = (double*)malloc( N * sizeof(double));
    

    for (int i = 0; i < N; ++i)
    {
        y1[i] = i % 256;
        y2[i] = i / 100;
    }

    for (int i = 0; i < N*N; ++i)
    {
        a[i] = i / 10;
    }

    runMvt_trace( a, x1, x2, y1, y2);
dumpMaxNumOfCL();
    return 0;
}
