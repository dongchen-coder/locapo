#include "../utility/rt.h"
#include "../utility/data_size.h"

#ifdef ORG
	#define NI 256
	#define NJ 256
	#define NK 256
	#define NL 256
#elif defined (TX)
#elif defined (FX)
#elif defined (EX)
#endif

#define TMP_OFFSET 0
#define A_OFFSET NI * NJ
#define B_OFFSET NI * NJ + NI * NK
#define D_OFFSET NI * NJ + NI * NK + NJ * NK
#define C_OFFSET NI * NJ + NI * NK + NJ * NK + NI * NL

void mm2_trace(double* tmp, double* A, double* B, double* C, double* D, double alpha, double beta) {

    int i, j, k;
    i = 0;
    k = 0;
    
        for (j = 0; j < 100; j++) {
            tmp[i * NJ + j] = 0.0;
			rtTmpAccess(TMP_OFFSET + i * NJ + j, 0, 0);
            if(j % 3 == 0){
                continue;
            }
            if (j % 2 == 0) {
                A[i * NK + k] = 4.0;
                rtTmpAccess(A_OFFSET + i * NK + k, 1, 1);
            }
        }
    
}


int main() {
	
	double* tmp = (double*)malloc( NI * NJ * sizeof(double));
	double* A = (double*)malloc( NI * NK * sizeof(double));
	double* B = (double*)malloc( NK * NJ * sizeof(double));
	double* C = (double*)malloc( NJ * NL * sizeof(double));
	double* D = (double*)malloc( NI * NL * sizeof(double));
	double alpha = 0.1;
	double beta = 0.5;
	
	mm2_trace(tmp, A, B, C, D, alpha, beta);

	dumpRtTmp();
    RTtoMR_AET();
    dumpMR();

	return 0;
}


