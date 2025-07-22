@echo off
echo ========================================
echo Configuration de Git LFS pour fire_app
echo ========================================

REM Vérifier si Git LFS est installé
git lfs version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Git LFS n'est pas installé !
    echo Téléchargez-le depuis: https://git-lfs.github.io/
    pause
    exit /b 1
)

echo 1. Initialisation de Git LFS...
git lfs install

echo 2. Suppression du fichier du cache Git...
git rm --cached data/fires_light.csv

echo 3. Configuration LFS pour les CSV volumineux...
git lfs track "*.csv"
git lfs track "data/*.csv"

echo 4. Ajout des fichiers de configuration...
git add .gitattributes

echo 5. Ajout du fichier CSV via LFS...
git add data/fires_light.csv

echo 6. Commit des modifications...
git commit -m "Configure Git LFS for large CSV files"

echo ========================================
echo Configuration terminée !
echo Vous pouvez maintenant faire: git push -u origin main
echo ========================================
pause
