#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <mpi.h>
#include <omp.h>

double wtime() {
    struct timeval t;
    gettimeofday(&t, NULL);
    return (double)t.tv_sec + (double)t.tv_usec * 1.0e-6;
}

int main(int argc, char *argv[]) {
    MPI_Init(&argc, &argv);
    
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (argc < 4) {
        if (rank == 0) {
            printf("Usage: mpirun -np <num_processes> ./hybrid_matmul N schedule_type num_threads [chunk_size]\n");
            printf("  N: ukuran matriks (N x N)\n");
            printf("  schedule_type: static, dynamic, atau guided\n");
            printf("  num_threads: jumlah thread OpenMP per proses\n");
            printf("  chunk_size: optional, default 1\n");
        }
        MPI_Finalize();
        return 1;
    }

    int N = atoi(argv[1]);
    char *schedule_type = argv[2];
    int num_threads = atoi(argv[3]);
    int chunk_size = (argc > 4) ? atoi(argv[4]) : 1;
    
    // Set jumlah thread OpenMP
    omp_set_num_threads(num_threads);
    
    // Each process handles a portion of rows
    int rows_per_process = N / size;
    int start_row = rank * rows_per_process;
    int end_row = (rank == size - 1) ? N : (rank + 1) * rows_per_process;
    int local_rows = end_row - start_row;

    double *A = malloc(N*N*sizeof(double));
    double *B = malloc(N*N*sizeof(double));
    double *C_local = malloc(local_rows*N*sizeof(double));
    double *C = NULL;

    if (rank == 0) {
        C = malloc(N*N*sizeof(double));
    }

    // Initialize matrices (all processes need full B matrix)
    for (int i=0;i<N*N;i++){
        A[i] = 1.0;
        B[i] = 1.0;
    }

    // Broadcast matrix B to all processes (if needed)
    MPI_Bcast(B, N*N, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    double total_start = wtime();
    double compute_start = wtime();

    // Parallel computation with OpenMP within each MPI process
    // Menggunakan schedule yang ditentukan
    if (strcmp(schedule_type, "static") == 0) {
        #pragma omp parallel for schedule(static, chunk_size)
        for (int i=0;i<local_rows;i++){
            int global_i = start_row + i;
            for (int j=0;j<N;j++){
                double sum = 0.0;
                for (int k=0;k<N;k++){
                    sum += A[global_i*N+k] * B[k*N+j];
                }
                C_local[i*N+j] = sum;
            }
        }
    } else if (strcmp(schedule_type, "dynamic") == 0) {
        #pragma omp parallel for schedule(dynamic, chunk_size)
        for (int i=0;i<local_rows;i++){
            int global_i = start_row + i;
            for (int j=0;j<N;j++){
                double sum = 0.0;
                for (int k=0;k<N;k++){
                    sum += A[global_i*N+k] * B[k*N+j];
                }
                C_local[i*N+j] = sum;
            }
        }
    } else if (strcmp(schedule_type, "guided") == 0) {
        #pragma omp parallel for schedule(guided, chunk_size)
        for (int i=0;i<local_rows;i++){
            int global_i = start_row + i;
            for (int j=0;j<N;j++){
                double sum = 0.0;
                for (int k=0;k<N;k++){
                    sum += A[global_i*N+k] * B[k*N+j];
                }
                C_local[i*N+j] = sum;
            }
        }
    } else {
        if (rank == 0) {
            printf("Invalid schedule type. Use: static, dynamic, or guided\n");
        }
        free(A); free(B); free(C_local);
        if (rank == 0) free(C);
        MPI_Finalize();
        return 1;
    }

    double compute_end = wtime();
    double compute_time = compute_end - compute_start;

    // Gather results from all processes
    double comm_start = wtime();
    if (rank == 0) {
        MPI_Gather(C_local, local_rows*N, MPI_DOUBLE, C, local_rows*N, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    } else {
        MPI_Gather(C_local, local_rows*N, MPI_DOUBLE, NULL, 0, MPI_DOUBLE, 0, MPI_COMM_WORLD);
    }
    double comm_end = wtime();
    double comm_time = comm_end - comm_start;

    double total_end = wtime();
    double total_time = total_end - total_start;

    if (rank == 0) {
        printf("Hybrid N=%d P=%d T=%d schedule=%s: total=%.6f compute=%.6f comm=%.6f\n", 
               N, size, num_threads, schedule_type, total_time, compute_time, comm_time);
    }

    free(A); free(B); free(C_local);
    if (rank == 0) free(C);

    MPI_Finalize();
    return 0;
}
