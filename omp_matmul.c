#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <omp.h>

double wtime() {
    struct timeval t;
    gettimeofday(&t, NULL);
    return (double)t.tv_sec + (double)t.tv_usec * 1.0e-6;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("Usage: ./omp_matmul N schedule_type [chunk_size]\n");
        printf("schedule_type: static, dynamic, guided\n");
        printf("chunk_size: optional, default 1\n");
        return 1;
    }

    int N = atoi(argv[1]);
    char *schedule_type = argv[2];
    int chunk_size = (argc > 3) ? atoi(argv[3]) : 1;

    double *A = malloc(N*N*sizeof(double));
    double *B = malloc(N*N*sizeof(double));
    double *C = malloc(N*N*sizeof(double));

    // Initialize matrices
    for (int i=0;i<N*N;i++){
        A[i] = 1.0;
        B[i] = 1.0;
    }

    double start = wtime();

    // Set schedule type
    if (strcmp(schedule_type, "static") == 0) {
        #pragma omp parallel for schedule(static, chunk_size)
        for (int i=0;i<N;i++){
            for (int j=0;j<N;j++){
                double sum = 0.0;
                for (int k=0;k<N;k++){
                    sum += A[i*N+k] * B[k*N+j];
                }
                C[i*N+j] = sum;
            }
        }
    } else if (strcmp(schedule_type, "dynamic") == 0) {
        #pragma omp parallel for schedule(dynamic, chunk_size)
        for (int i=0;i<N;i++){
            for (int j=0;j<N;j++){
                double sum = 0.0;
                for (int k=0;k<N;k++){
                    sum += A[i*N+k] * B[k*N+j];
                }
                C[i*N+j] = sum;
            }
        }
    } else if (strcmp(schedule_type, "guided") == 0) {
        #pragma omp parallel for schedule(guided, chunk_size)
        for (int i=0;i<N;i++){
            for (int j=0;j<N;j++){
                double sum = 0.0;
                for (int k=0;k<N;k++){
                    sum += A[i*N+k] * B[k*N+j];
                }
                C[i*N+j] = sum;
            }
        }
    } else {
        printf("Invalid schedule type. Use: static, dynamic, or guided\n");
        free(A); free(B); free(C);
        return 1;
    }

    double end = wtime();

    printf("OpenMP %s time: %.6f\n", schedule_type, end-start);

    free(A); free(B); free(C);
    return 0;
}

