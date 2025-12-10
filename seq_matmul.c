#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>

double wtime() {
    struct timeval t;
    gettimeofday(&t, NULL);
    return (double)t.tv_sec + (double)t.tv_usec * 1.0e-6;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: ./seq N\n");
        return 1;
    }

    int N = atoi(argv[1]);
    double *A = malloc(N*N*sizeof(double));
    double *B = malloc(N*N*sizeof(double));
    double *C = malloc(N*N*sizeof(double));

    for (int i=0;i<N*N;i++){
        A[i] = 1.0;
        B[i] = 1.0;
    }

    double start = wtime();

    for (int i=0;i<N;i++){
        for (int j=0;j<N;j++){
            double sum = 0.0;
            for (int k=0;k<N;k++){
                sum += A[i*N+k] * B[k*N+j];
            }
            C[i*N+j] = sum;
        }
    }

    double end = wtime();

    printf("Sequential time: %.6f\n", end-start);

    free(A); free(B); free(C);
    return 0;
}
