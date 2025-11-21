"""
SQLite veritabanını görüntülemek için basit bir script.
Kullanım: python view_db.py
"""
import sqlite3
import os

# Veritabanı yolu
db_path = os.path.join('instance', 'site.db')

if not os.path.exists(db_path):
    print(f"❌ Veritabanı dosyası bulunamadı: {db_path}")
    exit(1)

# Veritabanına bağlan
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("📊 VERİTABANI İÇERİĞİ")
print("=" * 60)

# Tüm tabloları listele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

if not tables:
    print("❌ Veritabanında tablo bulunamadı.")
else:
    for table in tables:
        table_name = table[0]
        print(f"\n📋 Tablo: {table_name}")
        print("-" * 60)
        
        # Tablo yapısını göster
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("Kolonlar:")
        for col in columns:
            col_name, col_type = col[1], col[2]
            print(f"  • {col_name} ({col_type})")
        
        # Tablodaki verileri göster
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        print(f"\n📝 Veriler ({len(rows)} kayıt):")
        if rows:
            # Kolon isimlerini al
            col_names = [description[0] for description in cursor.description]
            print(f"  {' | '.join(col_names)}")
            print("  " + "-" * 50)
            
            for row in rows:
                print(f"  {' | '.join(str(val) for val in row)}")
        else:
            print("  (Henüz veri yok)")

conn.close()
print("\n" + "=" * 60)
print("✅ Tamamlandı!")

