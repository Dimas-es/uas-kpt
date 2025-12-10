#!/bin/bash

# Script untuk menjalankan eksperimen Hybrid MPI-OpenMP
# dengan variasi: ukuran matriks, jumlah proses, jumlah thread, dan schedule OpenMP

RESULTS_FILE="experiment_results.txt"
DATA_FILE="experiment_data.txt"

# Ukuran matriks yang akan diuji
MATRIX_SIZES=(512 1024)

# Jumlah proses MPI
MPI_PROCS=(1 2 4)

# Jumlah thread OpenMP per proses
OMP_THREADS=(2 4 8)

# Schedule types
SCHEDULES=("static" "dynamic" "guided")

echo "=== Eksperimen Hybrid MPI-OpenMP ===" > $RESULTS_FILE
echo "Judul: Analisis Kinerja dan Efisiensi Komputasi pada Perkalian Matriks Skala Besar"
echo "      Menggunakan Hybrid MPI-OpenMP dengan Variasi Teknik OpenMP Scheduling"
echo "" >> $RESULTS_FILE
echo "Tanggal: $(date)" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE

# Inisialisasi file data
echo "# Data hasil eksperimen" > $DATA_FILE
echo "# Format: MATRIX_SIZE_MPI_PROCS_THREADS_SCHEDULE=total_time,compute_time,comm_time" >> $DATA_FILE
echo "" >> $DATA_FILE

# 1. Sequential baseline untuk setiap ukuran matriks
echo "=== Sequential Baseline ===" >> $RESULTS_FILE
for N in "${MATRIX_SIZES[@]}"; do
    echo "Running sequential for N=$N..."
    SEQ_OUTPUT=$(./seq_matmul $N 2>&1)
    echo "$SEQ_OUTPUT" >> $RESULTS_FILE
    SEQ_TIME=$(echo "$SEQ_OUTPUT" | grep "Sequential time:" | awk '{print $3}')
    echo "SEQ_${N}=$SEQ_TIME" >> $DATA_FILE
    echo "Sequential N=$N: $SEQ_TIME" >> $RESULTS_FILE
done
echo "" >> $RESULTS_FILE

# 2. Hybrid MPI-OpenMP dengan berbagai kombinasi
echo "=== Hybrid MPI-OpenMP Experiments ===" >> $RESULTS_FILE

for N in "${MATRIX_SIZES[@]}"; do
    echo "=== Matrix Size: $N x $N ===" >> $RESULTS_FILE
    echo "Testing matrix size: $N x $N..."
    
    for P in "${MPI_PROCS[@]}"; do
        for T in "${OMP_THREADS[@]}"; do
            for SCHED in "${SCHEDULES[@]}"; do
                echo "  Testing: P=$P, T=$T, Schedule=$SCHED"
                
                # Set environment variable untuk OpenMP
                export OMP_NUM_THREADS=$T
                
                # Jalankan hybrid program
                OUTPUT=$(mpirun -np $P ./hybrid_matmul $N $SCHED $T 1 2>&1)
                echo "$OUTPUT" >> $RESULTS_FILE
                
                # Parse output - format: Hybrid N=512 P=2 T=4 schedule=static: total=0.477366 compute=0.457070 comm=0.020294
                TOTAL_TIME=$(echo "$OUTPUT" | grep "Hybrid" | awk -F'total=' '{print $2}' | awk '{print $1}')
                COMPUTE_TIME=$(echo "$OUTPUT" | grep "Hybrid" | awk -F'compute=' '{print $2}' | awk '{print $1}')
                COMM_TIME=$(echo "$OUTPUT" | grep "Hybrid" | awk -F'comm=' '{print $2}')
                
                # Simpan ke data file
                KEY="${N}_${P}_${T}_${SCHED}"
                echo "${KEY}_total=$TOTAL_TIME" >> $DATA_FILE
                echo "${KEY}_compute=$COMPUTE_TIME" >> $DATA_FILE
                echo "${KEY}_comm=$COMM_TIME" >> $DATA_FILE
                
                echo "    Result: total=$TOTAL_TIME, compute=$COMPUTE_TIME, comm=$COMM_TIME" >> $RESULTS_FILE
            done
        done
    done
    echo "" >> $RESULTS_FILE
done

# 3. Summary
echo "=== Summary ===" >> $RESULTS_FILE
echo "Eksperimen selesai pada: $(date)" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE
echo "Kombinasi yang diuji:" >> $RESULTS_FILE
echo "  - Ukuran matriks: ${MATRIX_SIZES[@]}" >> $RESULTS_FILE
echo "  - Jumlah proses MPI: ${MPI_PROCS[@]}" >> $RESULTS_FILE
echo "  - Jumlah thread OpenMP: ${OMP_THREADS[@]}" >> $RESULTS_FILE
echo "  - Schedule OpenMP: ${SCHEDULES[@]}" >> $RESULTS_FILE

echo ""
echo "=== Eksperimen Selesai ==="
echo "Hasil lengkap: $RESULTS_FILE"
echo "Data untuk analisis: $DATA_FILE"
echo ""
echo "Menjalankan script visualisasi..."

# Jalankan script Python untuk membuat grafik
python3 plot_schedule.py
python3 grafik_proses.py

echo "Selesai!"
