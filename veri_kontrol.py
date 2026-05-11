import pandas as pd
import os

# 1. Dosya adını düzeltiyoruz: 'yilan_verisi.csv' dosyasını direkt hedef alalım
csv_file = 'yilan_verisi.csv'

if not os.path.exists(csv_file):
    print(f"❌ {csv_file} bulunamadı! Lütfen önce veri toplayın.")
    exit()

# 2. Veriyi oku
df = pd.read_csv(csv_file)

print(f"📂 Dosya: {csv_file}")
print(f"📊 Toplam Hamle Sayısı: {len(df)}\n")

# 3. Yeni formatımıza göre (action sütunu) dağılımı hesapla
# Main kodun 'LEFT', 'RIGHT', 'UP', 'DOWN' şeklinde kaydediyor
counts = df['action'].value_counts()

left_count  = counts.get('LEFT', 0)
right_count = counts.get('RIGHT', 0)
up_count    = counts.get('UP', 0)
down_count  = counts.get('DOWN', 0)
idle_count  = counts.get('IDLE', 0)

total_moves = left_count + right_count + up_count + down_count

print("🎮 TUŞ DAĞILIMI (Aksiyonlar):")
print(f"   ⬅️  SOL:    {left_count} kez (%{left_count/len(df)*100:.1f})")
print(f"   ➡️  SAĞ:    {right_count} kez (%{right_count/len(df)*100:.1f})")
print(f"   ⬆️  YUKARI: {up_count} kez (%{up_count/len(df)*100:.1f})")
print(f"   ⬇️  AŞAĞI:  {down_count} kez (%{down_count/len(df)*100:.1f})")
print(f"   🛑 DURMA:  {idle_count} kez (%{idle_count/len(df)*100:.1f})")

print(f"\n✅ Aktif hareket yüzdesi: %{(total_moves/len(df))*100:.1f}")

# 4. Mesafe Analizi (AI için ne kadar anlamlı veri var?)
avg_dx = df['dx'].abs().mean()
avg_dy = df['dy'].abs().mean()
print(f"📍 Ortalama Hedef Mesafesi (Mesafe ne kadar azsa veri o kadar kalitelidir):")
print(f"   DX: {avg_dx:.1f} piksel | DY: {avg_dy:.1f} piksel")