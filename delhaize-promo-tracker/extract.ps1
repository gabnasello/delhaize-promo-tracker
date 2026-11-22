# Turns saved Delhaize list pages (.htm) in saved_pages\ into data\favorites.csv
param([string]$Folder = "saved_pages")
Set-Location $PSScriptRoot
& .\.venv\Scripts\python.exe tools\html_to_csv.py $Folder
