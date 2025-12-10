CC = /usr/bin/gcc
MPICC = mpicc
CFLAGS = -Wall -O2
OMP_FLAGS = -fopenmp

# Default target
all: seq_matmul omp_matmul hybrid_matmul

# Sequential program
seq_matmul: seq_matmul.c
	$(CC) $(CFLAGS) -o seq_matmul seq_matmul.c

# OpenMP program
omp_matmul: omp_matmul.c
	$(CC) $(CFLAGS) $(OMP_FLAGS) -o omp_matmul omp_matmul.c

# Hybrid program (MPI + OpenMP)
hybrid_matmul: hybrid_matmul.c
	$(MPICC) $(CFLAGS) $(OMP_FLAGS) -o hybrid_matmul hybrid_matmul.c

# Clean
clean:
	rm -f seq_matmul omp_matmul hybrid_matmul *.o

# Run experiments
run: all
	bash run_experiments.sh

.PHONY: all clean run

