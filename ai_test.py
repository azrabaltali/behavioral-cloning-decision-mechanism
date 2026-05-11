import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

def test_ai_performance():
    # 1. Veri Kontrolü
    if not os.path.exists('yilan_verisi.csv'):
        print("❌ HATA: Test edilecek veri bulunamadı! Önce ana oyunda veri topla.")
        return

    # 2. Veri Hazırlama
    df = pd.read_csv('yilan_verisi.csv')
    
    # Özellik Mühendisliği (Main kodundakiyle aynı olmalı)
    df['abs_dx'] = df['dx'].abs()
    df['abs_dy'] = df['dy'].abs()
    df['manhattan'] = df['abs_dx'] + df['abs_dy']
    df['norm_dx'] = df['dx'] / (df['manhattan'] + 1)
    df['norm_dy'] = df['dy'] / (df['manhattan'] + 1)
    
    FEATURES = ['dx', 'dy', 'abs_dx', 'abs_dy', 'manhattan', 'norm_dx', 'norm_dy']
    X = df[FEATURES]
    y = df['action']

    print(f"📊 Toplam Örnek Sayısı: {len(df)}")
    print("-" * 40)

    # 3. Veriyi bölme (%80 Eğitim, %20 Test)
    # AI verinin %80'ine bakarak öğrenecek, hiç görmediği %20'lik kısımda seni taklit etmeye çalışacak.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Model Eğitimi
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 5. Tahmin ve Analiz
    y_pred = model.predict(X_test)
    isabet_orani = accuracy_score(y_test, y_pred)

    # --- RAPORLAMA ---
    print(f"✅ AI TAKLİT YETENEĞİ (Accuracy): %{isabet_orani * 100:.2f}")
    print("\n📝 Yön Bazlı Detaylı Analiz:")
    print(classification_report(y_test, y_pred))

    # Yorumlama
    if isabet_orani > 0.85:
        print("🚀 SONUÇ: Harika! AI senin neredeyse kopyan olmuş.")
    elif isabet_orani > 0.60:
        print("📈 SONUÇ: İyi gidiyor. AI temel mantığını çözmüş ama biraz daha veriye ihtiyacı var.")
    else:
        print("⚠️ SONUÇ: Zayıf taklit. Farklı durumlarda daha fazla oyun verisi toplamalısın.")

if __name__ == "__main__":
    test_ai_performance()