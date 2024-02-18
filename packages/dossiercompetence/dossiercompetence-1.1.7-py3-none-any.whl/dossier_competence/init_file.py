import os
import shutil
from pathlib import Path


def creer_dossier(nom_dossier: str):
    if not os.path.exists(nom_dossier):
        os.makedirs(nom_dossier)


def copy_file(source_dossier, cible_dossier, file_name):
    path = Path(__file__).parent
    path_copier = path / source_dossier / file_name
    path_coller = cible_dossier + "/" + file_name
    shutil.copyfile(path_copier, path_coller)


def main():
    creer_dossier("file_static")
    print("dossier créé")
    copy_file("static", "file_static", "pied.png")
    copy_file("static", "file_static", "Datalyo_logo_rvb.png")
    copy_file("static", "file_static", "test.css")
    print("fichiers prêt")


if __name__ == "__main__":
    main()
