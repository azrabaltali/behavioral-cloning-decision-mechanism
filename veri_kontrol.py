import pandas as pd
import os

csv_files = [f for f in os.listdir('.') if f.startswith('veri_') and f.endswith('.csv')]
if not csv_files:
    print("❌ Veri yok!")
    exit()

csv_file = max(csv_files, key=os.path.getctime)
df = pd.read_csv(csv_file)

print(f"📂 {csv_file}")
print(f"📊 Toplam {len(df)} hamle\n")

left_count = df['left'].sum()
right_count = df['right'].sum()
up_count = df['up'].sum()
down_count = df['down'].sum()

# DOĞRU hesaplama: toplam hareketli hamle sayısı
total_moves = left_count + right_count + up_count + down_count
no_move = len(df) - total_moves

print("🎮 TUŞ DAĞILIMI:")
print(f"   SOL:    {left_count} kez (%{left_count/len(df)*100:.1f})")
print(f"   SAĞ:    {right_count} kez (%{right_count/len(df)*100:.1f})")
print(f"   YUKARI: {up_count} kez (%{up_count/len(df)*100:.1f})")
print(f"   AŞAĞI:  {down_count} kez (%{down_count/len(df)*100:.1f})")
print(f"   HAREKET YOK: {no_move} kez (%{no_move/len(df)*100:.1f})")

print(f"\n✅ Toplam hareket: {total_moves} ({(total_moves/len(df))*100:.1f}%)")