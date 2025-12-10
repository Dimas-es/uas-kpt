import plotext as plt
import os
import re

# Coba baca data dari file experiment_data.txt
def load_schedule_data():
    data = {}
    if os.path.exists('experiment_data.txt'):
        with open('experiment_data.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle format yang mungkin: key=value atau key=comm=value
                if '=' in line:
                    # Split hanya di '=' pertama
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0]
                        value_str = parts[1]
                        
                        # Jika value mengandung "comm=", ambil angka setelahnya
                        if 'comm=' in value_str:
                            # Extract angka dari string
                            match = re.search(r'[\d.]+', value_str)
                            if match:
                                value_str = match.group()
                        
                        try:
                            data[key] = float(value_str)
                        except ValueError:
                            pass
    
    # Ambil data schedule untuk N=1024, P=2, T=4 (contoh representatif)
    # Atau gunakan rata-rata dari beberapa kombinasi
    static_times = []
    dynamic_times = []
    guided_times = []
    
    for key, value in data.items():
        if '_static_total' in key and not 'comm=' in str(value):
            static_times.append(value)
        elif '_dynamic_total' in key and not 'comm=' in str(value):
            dynamic_times.append(value)
        elif '_guided_total' in key and not 'comm=' in str(value):
            guided_times.append(value)
    
    # Ambil nilai representatif (misalnya untuk N=1024, P=2, T=4)
    # Atau gunakan rata-rata
    static_time = data.get('1024_2_4_static_total', 
                          sum(static_times)/len(static_times) if static_times else 9.66)
    dynamic_time = data.get('1024_2_4_dynamic_total',
                           sum(dynamic_times)/len(dynamic_times) if dynamic_times else 12.20)
    guided_time = data.get('1024_2_4_guided_total',
                          sum(guided_times)/len(guided_times) if guided_times else 10.31)
    
    # Jika tidak ada, coba ambil dari kombinasi lain
    if static_time == 9.66:
        # Cari kombinasi yang ada
        for key in data.keys():
            if '1024' in key and '_static_total' in key:
                static_time = data[key]
                break
    
    if dynamic_time == 12.20:
        for key in data.keys():
            if '1024' in key and '_dynamic_total' in key:
                dynamic_time = data[key]
                break
    
    if guided_time == 10.31:
        for key in data.keys():
            if '1024' in key and '_guided_total' in key:
                guided_time = data[key]
                break
    
    return {
        'STATIC_TIME': static_time,
        'DYNAMIC_TIME': dynamic_time,
        'GUIDED_TIME': guided_time
    }

data = load_schedule_data()

# Data dari hasil percobaan
labels = ["Static", "Dynamic", "Guided"]
times = [data['STATIC_TIME'], data['DYNAMIC_TIME'], data['GUIDED_TIME']]

plt.bar(labels, times)
plt.title("Perbandingan Waktu Eksekusi berdasarkan Schedule OMP")
plt.xlabel("Schedule")
plt.ylabel("Waktu (detik)")

plt.show()
