from .cv import CV
import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convertir le fichier Markdown en fichier HTML ou PDF."
    )
    parser.add_argument(
        "-i", "--inputMD", type=str, help="Entrer le répertoire du fichier.md"
    )
    parser.add_argument(
        "-style", "--liencss", type=str, help="Entrer le répertoire du fichier.css" # noqa:
    )
    parser.add_argument(
        "-a",
        "--anonimize",
        action="store_true",
        help="sortir le fichier anonyme",
        default=False,
    )
    parser.add_argument(
        "-html",
        "--toHtml",
        action="store_true",
        help="sortir le fichier html",
        default=False,
    )
    parser.add_argument(
        "-pdf",
        "--toPdf",
        action="store_true",
        help="sortir le fichier pdf",
        default=False,
    )
    parser.add_argument(
        "-all",
        "--toAll",
        action="store_true",
        help="sortir tous les fichiers",
        default=False,
    )
    args = parser.parse_args()
    return args


def creer_dossier(nom_dossier: str):
    if not os.path.exists(nom_dossier):
        os.makedirs(nom_dossier)


def get_class_cv(input_file_md: str):
    with open(input_file_md, "r") as input_md:
        cv_str = input_md.read()
    return CV(cv_str)


class TrigrammerError(Exception):
    pass


def trigrammer(nom_prenom: str):
    """Trigrammer le nom et prenom et creer une dossier named trigramme

    :example :
    >>> print(trigrammer("yao.xin"))
    xya
    """
    try:
        nom = nom_prenom.split(".")[0]
        prenom = nom_prenom.split(".")[1]
        t_nom = nom[0] + nom[1]
        t_prenom = prenom[0]
    except IndexError:
        raise TrigrammerError("wrong format, need to use firstname.name")
    trigramme = t_prenom + t_nom
    return trigramme


def file_name_anonimized(file_md: str) -> str:
    """Anonimize le nom de fichier

    :example :
    >>> print(file_name_anonimized("dataScience.md"))
    dataScience_a
    """
    file_name = file_md.split(".md")[0]
    file_name_output = file_name + "_a"
    return file_name_output


def file_name(file_md: str) -> str:
    """afficher le nom de fichier

    :example :
    >>> print(file_name("dataScience.md"))
    dataScience
    """
    file_name = file_md.split(".md")[0]
    file_name_output = file_name
    return file_name_output


def get_trigrammer(input_md: str) -> str:
    """Récupérez la partie à trigrammer du input

    :example :
    >>> get_trigrammer("yao.xin/dataScience.md")
    yao.xin
    """
    try:
        a_trigrammer = input_md.split("/")[-2]
    except IndexError:
        raise TrigrammerError("wrong format, need to use firstname.name/metier.md") # noqa:
    return a_trigrammer


def get_file_name(input_md: str) -> str:
    """Récupérez la partie metier du input

    :example :
    >>> get_file_name("yao.xin/dataScience.md")
    dataScience.md
    """
    try:
        file_name_o = input_md.split("/")[-1]
    except IndexError:
        raise TrigrammerError("wrong format, need to use firstname.name/metier.md") # noqa:
    return file_name_o


def get_output_name(input_md: str, anonimized: bool):
    trigramme = trigrammer(get_trigrammer(input_md))
    creer_dossier(trigramme)
    filename = file_name(get_file_name(input_md))
    file_name_a = file_name_anonimized(get_file_name(input_md))
    if anonimized is True:
        output_name = trigramme + "/" + file_name_a
    else:
        output_name = trigramme + "/" + filename
    return output_name


def main():
    args = parse_args()
    cv = get_class_cv(args.inputMD)
    cv_anonimized = get_class_cv(args.inputMD).anonimize()
    if args.toAll:
        cv_anonimized.to_html_file(
            get_output_name(args.inputMD, anonimized=True), args.liencss
        )
        cv_anonimized.to_pdf_file(
            get_output_name(args.inputMD, anonimized=True), args.liencss
        )
        cv.to_html_file(get_output_name(args.inputMD, anonimized=False), args.liencss) # noqa:
        cv.to_pdf_file(get_output_name(args.inputMD, anonimized=False), args.liencss) # noqa:
    if args.anonimize:
        if args.toHtml:
            cv_anonimized.to_html_file(
                get_output_name(args.inputMD, anonimized=True), args.liencss
            )
        if args.toPdf:
            cv_anonimized.to_pdf_file(
                get_output_name(args.inputMD, anonimized=True), args.liencss
            )
    else:
        if args.toHtml:
            cv.to_html_file(
                get_output_name(args.inputMD, anonimized=False), args.liencss
            )
        if args.toPdf:
            cv.to_pdf_file(
                get_output_name(args.inputMD, anonimized=False), args.liencss
            )


if __name__ == "__main__":
    main()
