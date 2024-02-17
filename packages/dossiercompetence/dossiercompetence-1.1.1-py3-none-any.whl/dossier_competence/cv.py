import markdown
from weasyprint import HTML, CSS
import json
import os


class CV:
    """class pour manipuler un contenu du cv

    :example :
    >>> cv = CV("# Test markdown")
    >>> cv.to_html_content()
    "<h1> Test markdown</h1>"
    >>> cv.to_pdf_file()
    >>> cv.anonimize({"Test":"A"})
    CV("#A markdown")

    """

    def __init__(
        self,
        md: str,
        html_template="dossier_competence/webBlanche.html",
        fileAnomyme="dossier_competence/anonyme.json",
        logo_tete="file_static/Datalyo_logo_rvb.png",
        logo_pied="file_static/pied.png",
    ) -> None:
        """initialise le contenu du cv"""
        current_path = os.path.abspath(__file__)
        father_path = os.path.abspath(
            os.path.dirname(current_path) + os.path.sep + ".."
        )
        self.md = md
        self.html_template = os.path.join(father_path, html_template)
        self.fileAnomyme = os.path.join(father_path, fileAnomyme)
        self.logo_tete_html = "../" + logo_tete
        self.logo_pied_html = "../" + logo_pied
        self.logo_tete_pdf = logo_tete
        self.logo_pied_pdf = logo_pied

    def to_html_content(self, css_lien, for_pdf: bool):
        """transformer le format md en html"""
        cv_content = markdown.markdown(self.md)
        with open(self.html_template, "r", encoding="utf-8") as html_blanche:
            html_content = html_blanche.read().replace("CV", cv_content)
            css_lien = "../" + css_lien
            html_content = html_content.replace("LIEN_CSS", css_lien)
            if for_pdf is True:
                html_content = html_content.replace("LOGO_TETE", self.logo_tete_pdf) # noqa:
                html_content = html_content.replace("LOGO_PIED", self.logo_pied_pdf) # noqa:
            else:
                html_content = html_content.replace("LOGO_TETE", self.logo_tete_html) # noqa:
                html_content = html_content.replace("LOGO_PIED", self.logo_pied_html) # noqa:
        return html_content

    def to_html_file(self, output_html_file, css_lien):
        """transformer le format md en html et sorti la fichier.html"""
        html_content = self.to_html_content(css_lien, for_pdf=False)
        output_html_file = output_html_file + ".html"
        with open(output_html_file, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)

    def to_pdf_file(self, output_pdf_file, css_lien):
        """transformer le format html en pdf et sorti la fichier.pdf"""
        html = HTML(string=self.to_html_content(css_lien, for_pdf=True), base_url="") # noqa:
        output_pdf_file = output_pdf_file + ".pdf"
        with open(css_lien, "rb") as f:
            css = f.read()
            html.write_pdf(
                output_pdf_file,
                stylesheets=[CSS(string=css)],
                presentational_hints=True,
            )

    def anonimize(self):
        """anonimiser le contenu du cv"""
        cv_anonimized = self.md
        with open(self.fileAnomyme, "r") as anonimizeFile:
            dictAnonimizd = json.loads(anonimizeFile.read())
        for key in dictAnonimizd:
            cv_anonimized = cv_anonimized.replace(key, dictAnonimizd[key])
        return CV(cv_anonimized)
