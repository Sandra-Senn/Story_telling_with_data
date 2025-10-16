# Story_telling_with_data

This repository was created for the module "Storytelling with Data" at FHNW during the spring semester 2025. The core focus is a web data story that illustrates the impact of climate change on fish in Switzerland, especially regarding their survival duration as temperatures rise.

---

## Project Overview

- **Web Data Story:**  
  Multimedia presentation located in the `webstory_fisch` folder, entry point is `index.html`.
- **Python Scripts:**  
  Data transformation, visualization, and web scraping in the `src/` folder.
- **Data:**  
  Analysis results, raw data, and legal texts in the `data/` folder.
- **Jupyter Notebooks:**  
  Data exploration and analysis in the `notebooks/` folder.

---

## Viewing the Web Data Story

### With Visual Studio Code & Live Server (recommended)

1. Ensure VS Code and the **Live Server** extension are installed.
2. Open the project in VS Code.
3. Navigate to the `webstory_fisch` folder and open the `index.html` file.
4. Right-click `index.html` → select **"Open with Live Server"**.
5. A browser window will open with the web data story.  
   Changes will be displayed instantly on save[web:12][web:3][web:4].

### Directly in the Browser (without editor)

#### Windows

- Open the `webstory_fisch` folder in the file explorer.
- Double click `index.html`.
- The page will open in your default browser (e.g. Edge, Chrome)[web:4].

#### Mac / Linux

- Open the `webstory_fisch` folder in your file manager.
- Double click `index.html`, or
- Right-click → "Open with..." and choose your browser[web:4].

> Interactive features work most reliably using VS Code Live Server.

---

## Project Structure

```bash
Story_telling_with_data/
├── data/                      # All data, raw data & results
│   ├── img_webscrape/
│   │   └── img_scraper/
│   ├── see_data/
│   ├── see_data_json/
│   ├── See_Temperatur_transformiert/
│   ├── working_files/
│   ├── Bundesgesetz_über_Fischerei.pdf
│   ├── df_merged.csv
│   ├── Fischdaten_final.csv
│   ├── Fischdaten_gemappt.csv
│   ├── Fischdaten_info_final.csv
│   ├── Fischdaten.csv
│   ├── Gefaehrdungsstatus_Codes.csv
│   ├── kritische_temperaturen.csv
│   ├── see_lat_lon_final.csv
│   └── temperaturdaten_kombiniert.csv
├── notebooks/                      # Jupyter Notebooks
│   ├── daw.ipynb
│   ├── eda.ipynb
│   └── See-daten-M.ipynb
├── src/                      # Python scripts (data transformation, visualization)                      
│   ├── __pycache__/
│   ├── fix_csv_pro.py
│   ├── fix_final_csv.py
│   ├── visualisation.py
│   └── z_image_scraper.py
├── webstory_fisch/                       # Web data story (HTML, CSS, JS, images)
│   ├── img/
│   ├── index.html
│   ├── script.js
│   ├── See-daten.ipynb
│   ├── style.css
│   ├── temperatur_plot.html
│   └── zeichnende_linien.html
├── .gitignore                      # Python dependencies 
├── README.md                      # This documentation
└── requirements.txt                      # Excluded files
```

---

## License & Usage

This project was created as part of studies at FHNW.  
Feel free to use it for your own research or teaching – please retain source attributions.

---
