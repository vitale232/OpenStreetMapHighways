call D:\Program_Files\miniconda3\condabin\activate.bat osmdiff_viewer
python D:\OpenStreetMap\ExtractNewYork\download_and_extract_osm.py
timeout 5
call conda deactivate
