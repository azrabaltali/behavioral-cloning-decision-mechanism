import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler

# ── Tüm CSV'leri topla ────────────────────────────────────────
csv_files = sorted(
    [f for f in os.listdir('.') if f.startswith('veri_') and f.endswith('.csv')]
)

if not csv_files:
    print("❌ Hiç veri dosyası (veri_*.csv) bulunamadı!")
    print("   Önce 'python veri_topla.py' çalıştırıp veri topla.")
    exit(1)

print(f"📂 {len(csv_files)} veri dosyası bulundu:")
dfs = []
for f in csv_files:
    df_temp = pd.read_csv(f)
    print(f"   • {f}  →  {len(df_temp)} hamle")
    dfs.append(df_temp)

df = pd.concat(dfs, ignore_index=True)
print(f"\n📊 Toplam {len(df)} hamle birleştirildi.\n")

# ── Etiket oluştur ────────────────────────────────────────────
def get_action(row):
    if row['left']  == 1: return 'LEFT'
    if row['right'] == 1: return 'RIGHT'
    if row['up']    == 1: return 'UP'
    if row['down']  == 1: return 'DOWN'
    return 'IDLE'

df['action'] = df.apply(get_action, axis=1)

# ── IDLE verisini dengele ─────────────────────────────────────
# IDLE %48 → modeli tembelleştiriyor. Hareket verileriyle eşitle.
idle_df  = df[df['action'] == 'IDLE']
move_df  = df[df['action'] != 'IDLE']
# IDLE sayısını hareket sayısıyla eşit tut (maksimum)
idle_cap = min(len(idle_df), len(move_df))
idle_df  = idle_df.sample(idle_cap, random_state=42)
df       = pd.concat([move_df, idle_df]).sample(frac=1, random_state=42).reset_index(drop=True)
print(f"   → IDLE dengelendi: {idle_cap} IDLE + {len(move_df)} hareket = {len(df)} toplam")

# Sınıf dağılımını göster
print("🎮 Sınıf dağılımı:")
dist = df['action'].value_counts()
for cls, cnt in dist.items():
    bar = "█" * int(cnt / len(df) * 40)
    print(f"   {cls:6s}  {cnt:5d}  {bar}  %{cnt/len(df)*100:.1f}")

# ── Özellikler ────────────────────────────────────────────────
# SADECE göreceli özellikler kullan (dx, dy, vs.)
# Ham player_x/y ve target_x/y ÇIKARILDI — model pozisyon ezberleyemez
df['dx']       = df['target_x'] - df['player_x']
df['dy']       = df['target_y'] - df['player_y']
df['abs_dx']   = df['dx'].abs()
df['abs_dy']   = df['dy'].abs()
df['manhattan']= df['abs_dx'] + df['abs_dy']
df['dx_norm']  = df['dx'] / (df['manhattan'] + 1)   # normalize yön
df['dy_norm']  = df['dy'] / (df['manhattan'] + 1)

FEATURES = ['dx', 'dy', 'abs_dx', 'abs_dy', 'manhattan', 'dx_norm', 'dy_norm']

X = df[FEATURES]
y = df['action']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Model eğit ────────────────────────────────────────────────
print("\n🌲 RandomForest eğitiliyor...")
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred    = model.predict(X_test)
accuracy  = accuracy_score(y_test, y_pred)
print(f"✅ Test doğruluğu: {accuracy:.2%}")

# 5-katlı çapraz doğrulama
cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy', n_jobs=-1)
print(f"📈 5-katlı CV: {cv_scores.mean():.2%} ± {cv_scores.std():.2%}")

# Detaylı rapor
print("\n📋 Sınıf bazlı rapor:")
print(classification_report(y_test, y_pred, zero_division=0))

# Özellik önemi
print("🔍 En önemli özellikler:")
importances = sorted(zip(FEATURES, model.feature_importances_),
                     key=lambda x: -x[1])
for feat, imp in importances:
    bar = "█" * int(imp * 60)
    print(f"   {feat:12s}  {bar}  {imp:.3f}")

# ── Kaydet ────────────────────────────────────────────────────
with open('ai_model.pkl', 'wb') as f:
    pickle.dump({'model': model, 'features': FEATURES}, f)

print(f"\n💾 Model kaydedildi: ai_model.pkl")
print(f"   Özellikler: {FEATURES}")