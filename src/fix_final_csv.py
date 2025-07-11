import pandas as pd


# Ursprüngliche kaputte Datei
df_raw = pd.read_csv("data/working_files/see_lat_lon.csv", header=None)

# Headerzeile + Daten splitten
df_split = df_raw[0].str.split(",", expand=True)

# Spaltennamen setzen
df_split.columns = ["See", "Latitude", "Longitude"]

# Doppelte Header-Zeile entfernen
df_clean = df_split[df_split["Latitude"] != '"Latitude"'].copy()

# Anführungszeichen + Leerzeichen entfernen
df_clean = df_clean.applymap(lambda x: x.replace('"', '').strip())

# Umwandeln in float
df_clean["Latitude"] = df_clean["Latitude"].astype(float)
df_clean["Longitude"] = df_clean["Longitude"].astype(float)

# Speichern
df_clean.to_csv("data/see_lat_lon_final.csv", index=False)

print("✅ Datei erfolgreich bereinigt & gespeichert!")
print(df_clean.head())
