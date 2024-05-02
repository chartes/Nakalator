# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""Ce script permet d'ajouter un préfixe aux noms de fichiers d'un dossier source,
de les copier dans un dossier cible, et de générer un fichier CSV de
mapping entre les anciens et nouveaux noms de fichiers.
"""

import os
import csv
import argparse
from pathlib import Path
import shutil

def standardize_filenames(source_folder, prefix, max_length):
    for filename in os.listdir(source_folder):
        if os.path.isfile(os.path.join(source_folder, filename)):
            # Extrait le numéro du nom de fichier et le reformate
            num = ''.join(filter(str.isdigit, filename))
            if num.isdigit():
                new_num = num.zfill(max_length)
                new_filename = prefix + new_num + os.path.splitext(filename)[1]
                yield filename, new_filename
            else:
                yield filename, prefix + filename

def add_prefix_and_move(source_folder, target_folder, prefix, standardize=False):
    # Trouve la longueur nécessaire pour standardiser les noms de fichiers
    if standardize:
        max_length = max(len(''.join(filter(str.isdigit, f))) for f in os.listdir(source_folder) if f.isdigit() or ''.join(filter(str.isdigit, f)))
    else:
        max_length = 0

    # Crée le dossier cible s'il n'existe pas
    Path(target_folder).mkdir(parents=True, exist_ok=True)

    # Prépare le fichier CSV pour le mapping
    csv_filename = os.path.join(target_folder, "mapping.csv")
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['original_name', 'new_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        # Génère de nouveaux noms de fichiers et les copie
        for original_name, new_name in standardize_filenames(source_folder, prefix, max_length):
            original_path = os.path.join(source_folder, original_name)
            new_path = os.path.join(target_folder, new_name)

            # Copie le fichier
            shutil.copy2(original_path, new_path)

            # Écrit le mapping dans le CSV
            writer.writerow({'original_name': original_name, 'new_name': new_name})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ajoute un préfixe aux noms de fichiers, les déplace, et optionnellement standardise les noms.")
    parser.add_argument("source", help="Chemin du dossier source")
    parser.add_argument("target", help="Chemin du dossier cible")
    parser.add_argument("prefix", help="Préfixe à ajouter aux noms de fichiers")
    parser.add_argument("-s", "--standardize", action="store_true", help="Active la standardisation des noms de fichiers (nombre: 1 -> 0001 ou 001)")

    args = parser.parse_args()

    add_prefix_and_move(args.source, args.target, args.prefix, args.standardize)