import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

csv_files = [f for f in os.listdir('.') if f.startswith('veri_') and f.endswith('.csv')]
if not csv_files:
    print("❌ Veri yok!")
    exit()

csv_file = max(csv_files, key=os.path.getctime)
df = pd.read_csv(csv_file)
print(f"📂 {csv_file} - {len(df)} hamle")

def get_action(row):
    if row['left'] == 1: return 'LEFT'
    if row['right'] == 1: return 'RIGHT'
    if row['up'] == 1: return 'UP'
    if row['down'] == 1: return 'DOWN'
    return 'IDLE'

df['action'] = df.apply(get_action, axis=1)

X = df[['player_x', 'player_y', 'target_x', 'target_y']]
y = df['action']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Daha basit model: daha az ağaç, max_depth sınırlı
model = RandomForestClassifier(n_estimators=30, max_depth=10, random_state=42)
model.fit(X_train, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test))
print(f"✅ Model doğruluğu: {accuracy:.2%}")

with open('ai_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("💾 Kaydedildi")