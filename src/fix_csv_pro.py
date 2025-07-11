import pandas as pd

# Ursprüngliche Datei (mit falscher Struktur)
df_raw = pd.read_csv("data/working_files/see_lat_lon.csv", header=None)

# Aufteilen mit Komma als Trennzeichen
df_split = df_raw[0].str.split(",", expand=True)

# Spaltennamen setzen
df_split.columns = ["See", "Latitude", "Longitude"]

# Werte bereinigen (Anführungszeichen & Leerzeichen)
df_split = df_split.applymap(lambda x: x.strip().replace('"', ''))

# In neue saubere Datei schreiben
df_split.to_csv("data/working_files/see_lat_lon_clean.csv", index=False)

print("✅ FIXED: see_lat_lon_clean.csv erstellt!")
print(df_split.head())
