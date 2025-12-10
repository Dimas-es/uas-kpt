# Hybrid MPI–OpenMP Matrix Multiplication

Proyek ini membandingkan kinerja perkalian matriks skala besar pada tiga pendekatan:
- `seq_matmul`: implementasi sekuensial sebagai baseline.
- `omp_matmul`: paralelisasi berbasis OpenMP dengan variasi schedule.
- `hybrid_matmul`: kombinasi MPI + OpenMP untuk distribusi baris matriks antar proses.

Eksperimen otomatis menghasilkan log, data numerik, serta grafik analisis performa/scheduling.

## Kebutuhan
- GCC dengan dukungan OpenMP.
- MPI (mis. OpenMPI/MPICH) untuk menjalankan `mpirun`.
- Python 3 + paket: `matplotlib`, `plotext` (untuk grafik terminal opsional), serta modul standar.

## Build
```bash
make            # membangun semua binari
make clean      # hapus binari hasil build
```

## Cara menjalankan program secara manual
- Baseline sekuensial:
  ```bash
  ./seq_matmul <N>
  # contoh: ./seq_matmul 512
  ```
- OpenMP dengan variasi schedule (opsional `chunk_size`, default 1):
  ```bash
  ./omp_matmul <N> <static|dynamic|guided> [chunk_size]
  # contoh: ./omp_matmul 1024 static 4
  ```
- Hybrid MPI + OpenMP (set `OMP_NUM_THREADS` atau argumen ketiga untuk jumlah thread):
  ```bash
  mpirun -np <proses> ./hybrid_matmul <N> <static|dynamic|guided> <num_threads> [chunk_size]
  # contoh: mpirun -np 4 ./hybrid_matmul 1024 dynamic 4 2
  ```

## Menjalankan seluruh eksperimen
Script `run_experiments.sh` akan:
1) Menjalankan baseline sekuensial untuk setiap `N` yang disetel.
2) Mencoba kombinasi ukuran matriks, jumlah proses, jumlah thread, dan jenis schedule pada program hybrid.
3) Menyimpan hasil ke file teks dan membuat grafik.

Jalankan:
```bash
make run
# atau langsung: bash run_experiments.sh
```

### Hasil keluaran
- `experiment_results.txt` : log terformat semua percobaan.
- `experiment_data.txt`    : pasangan key/value untuk analisis dan plotting.
- `hybrid_analysis.png`    : analisis lengkap (waktu total/compute, speedup, efisiensi).
- `schedule_comparison_by_size.png` : perbandingan schedule untuk berbagai ukuran matriks.
- `thread_scaling.png`     : efek variasi jumlah thread.
- `hybrid_analysis` juga dicetak ke terminal saat plotting dijalankan.

## Visualisasi ulang
Jika ingin menggambar ulang grafik tanpa menjalankan ulang eksperimen:
```bash
python3 plot_schedule.py   # grafik ASCII sederhana (plotext) berbasis data
python3 grafik_proses.py   # grafik .png analisis performa
```
Pastikan `experiment_data.txt` tersedia di direktori yang sama.

## Catatan implementasi
- Matriks A dan B diisi dengan 1.0 untuk memfokuskan pengukuran pada biaya komputasi/komunikasi.
- Program hybrid membagi baris matriks secara rata antar proses MPI, lalu tiap proses memakai OpenMP sesuai `schedule` dan `chunk_size` yang dipilih.
- Variasi default eksperimen dapat diubah di `run_experiments.sh` (arrays `MATRIX_SIZES`, `MPI_PROCS`, `OMP_THREADS`, `SCHEDULES`).

