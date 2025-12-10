import matplotlib.pyplot as plt
import os
import re

# Fungsi untuk membaca data dari file
def load_experiment_data():
    data = {}
    if os.path.exists('experiment_data.txt'):
        with open('experiment_data.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Handle format yang salah: jika value mengandung "comm=" atau "compute=", extract angka
                    if 'comm=' in value or 'compute=' in value or 'total=' in value:
                        # Extract angka dari string (ambil angka pertama yang ditemukan)
                        match = re.search(r'[\d.]+', value)
                        if match:
                            value = match.group()
                    try:
                        data[key] = float(value)
                    except ValueError:
                        pass
    return data

data = load_experiment_data()

# Ukuran matriks yang diuji
matrix_sizes = [512, 1024]
mpi_procs = [1, 2, 4]
omp_threads = [2, 4, 8]
schedules = ['static', 'dynamic', 'guided']

# 1. Grafik: Waktu Total vs Jumlah Proses untuk berbagai schedule (untuk N=1024)
print("Membuat grafik analisis performa...")

# Grafik 1: Perbandingan Schedule untuk N=1024, T=4
N = 1024
T = 4
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Subplot 1: Waktu Total vs Jumlah Proses (berbagai schedule)
ax1 = axes[0, 0]
for sched in schedules:
    times = []
    for P in mpi_procs:
        key = f"{N}_{P}_{T}_{sched}_total"
        if key in data:
            times.append(data[key])
        else:
            times.append(None)
    ax1.plot(mpi_procs, times, marker='o', label=f'{sched.capitalize()}', linewidth=2, markersize=8)
ax1.set_xlabel('Jumlah Proses MPI', fontsize=11)
ax1.set_ylabel('Waktu Total (s)', fontsize=11)
ax1.set_title(f'Waktu Total vs Jumlah Proses MPI\n(N={N}, Thread={T})', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Subplot 2: Waktu Komputasi vs Jumlah Proses
ax2 = axes[0, 1]
for sched in schedules:
    times = []
    for P in mpi_procs:
        key = f"{N}_{P}_{T}_{sched}_compute"
        if key in data:
            times.append(data[key])
        else:
            times.append(None)
    ax2.plot(mpi_procs, times, marker='s', label=f'{sched.capitalize()}', linewidth=2, markersize=8)
ax2.set_xlabel('Jumlah Proses MPI', fontsize=11)
ax2.set_ylabel('Waktu Komputasi (s)', fontsize=11)
ax2.set_title(f'Waktu Komputasi vs Jumlah Proses MPI\n(N={N}, Thread={T})', fontsize=12)
ax2.legend()
ax2.grid(True, alpha=0.3)

# Subplot 3: Speedup vs Jumlah Proses
ax3 = axes[1, 0]
# Hitung speedup berdasarkan waktu sequential
seq_key = f"SEQ_{N}"
if seq_key in data:
    seq_time = data[seq_key]
    for sched in schedules:
        speedups = []
        for P in mpi_procs:
            key = f"{N}_{P}_{T}_{sched}_total"
            if key in data:
                speedup = seq_time / data[key]
                speedups.append(speedup)
            else:
                speedups.append(None)
        ax3.plot(mpi_procs, speedups, marker='^', label=f'{sched.capitalize()}', linewidth=2, markersize=8)
    ax3.set_xlabel('Jumlah Proses MPI', fontsize=11)
    ax3.set_ylabel('Speedup', fontsize=11)
    ax3.set_title(f'Speedup vs Jumlah Proses MPI\n(N={N}, Thread={T})', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    # Tambahkan garis ideal
    ideal_speedup = [p * T for p in mpi_procs]
    ax3.plot(mpi_procs, ideal_speedup, 'k--', label='Ideal', alpha=0.5)

# Subplot 4: Efficiency vs Jumlah Proses
ax4 = axes[1, 1]
if seq_key in data:
    seq_time = data[seq_key]
    for sched in schedules:
        efficiencies = []
        for P in mpi_procs:
            key = f"{N}_{P}_{T}_{sched}_total"
            if key in data:
                speedup = seq_time / data[key]
                efficiency = speedup / (P * T)
                efficiencies.append(efficiency)
            else:
                efficiencies.append(None)
        ax4.plot(mpi_procs, efficiencies, marker='d', label=f'{sched.capitalize()}', linewidth=2, markersize=8)
    ax4.set_xlabel('Jumlah Proses MPI', fontsize=11)
    ax4.set_ylabel('Efficiency', fontsize=11)
    ax4.set_title(f'Efficiency vs Jumlah Proses MPI\n(N={N}, Thread={T})', fontsize=12)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='Ideal (100%)')

plt.tight_layout()
plt.savefig("hybrid_analysis.png", dpi=300, bbox_inches='tight')
plt.close()

# Grafik 2: Perbandingan Schedule untuk berbagai ukuran matriks
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
T = 4
P = 2

for idx, N in enumerate(matrix_sizes):
    ax = axes[idx]
    schedules_data = []
    labels = []
    
    for sched in schedules:
        key = f"{N}_{P}_{T}_{sched}_total"
        if key in data:
            schedules_data.append(data[key])
            labels.append(sched.capitalize())
    
    if schedules_data:
        bars = ax.bar(labels, schedules_data, color=['#3498db', '#e74c3c', '#2ecc71'])
        ax.set_ylabel('Waktu Total (s)', fontsize=10)
        ax.set_title(f'Perbandingan Schedule\nN={N}, P={P}, T={T}', fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        
        # Tambahkan nilai di atas bar
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}s', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig("schedule_comparison_by_size.png", dpi=300, bbox_inches='tight')
plt.close()

# Grafik 3: Scaling dengan berbagai jumlah thread
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
N = 1024
P = 2

# Subplot 1: Waktu vs Jumlah Thread
ax1 = axes[0]
for sched in schedules:
    times = []
    for T in omp_threads:
        key = f"{N}_{P}_{T}_{sched}_total"
        if key in data:
            times.append(data[key])
        else:
            times.append(None)
    ax1.plot(omp_threads, times, marker='o', label=f'{sched.capitalize()}', linewidth=2, markersize=8)
ax1.set_xlabel('Jumlah Thread OpenMP', fontsize=11)
ax1.set_ylabel('Waktu Total (s)', fontsize=11)
ax1.set_title(f'Waktu vs Jumlah Thread OpenMP\n(N={N}, P={P})', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# Subplot 2: Speedup vs Jumlah Thread
ax2 = axes[1]
seq_key = f"SEQ_{N}"
if seq_key in data:
    seq_time = data[seq_key]
    for sched in schedules:
        speedups = []
        for T in omp_threads:
            key = f"{N}_{P}_{T}_{sched}_total"
            if key in data:
                speedup = seq_time / data[key]
                speedups.append(speedup)
            else:
                speedups.append(None)
        ax2.plot(omp_threads, speedups, marker='s', label=f'{sched.capitalize()}', linewidth=2, markersize=8)
    ax2.set_xlabel('Jumlah Thread OpenMP', fontsize=11)
    ax2.set_ylabel('Speedup', fontsize=11)
    ax2.set_title(f'Speedup vs Jumlah Thread OpenMP\n(N={N}, P={P})', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("thread_scaling.png", dpi=300, bbox_inches='tight')
plt.close()

print("Grafik berhasil dibuat:")
print("- hybrid_analysis.png (analisis lengkap)")
print("- schedule_comparison_by_size.png (perbandingan schedule)")
print("- thread_scaling.png (scaling dengan thread)")
