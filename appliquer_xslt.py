"""
appliquer_xslt.py
=================
Applique la transformation XSLT sur le XML de résultats
pour produire le rapport HTML final.
"""

from lxml import etree


def transformer_xml_en_html(xml_file, xslt_file, html_file):
    """Lit le XML et le XSLT, puis écrit le HTML transformé."""

    # Charger le XML de résultats
    xml_doc = etree.parse(xml_file)

    # Charger la feuille de style XSLT
    xslt_doc = etree.parse(xslt_file)
    transform = etree.XSLT(xslt_doc)

    # Appliquer la transformation
    html_resultat = transform(xml_doc)

    # Écrire le fichier HTML
    with open(html_file, "wb") as f:
        f.write(etree.tostring(html_resultat, pretty_print=True, method="html"))

    print(f"[OK] Rapport HTML généré : {html_file}")


if __name__ == "__main__":
    transformer_xml_en_html(
        xml_file="resultats_credit.xml",
        xslt_file="rapport.xslt",
        html_file="rapport_credit.html"
    )
    print("[INFO] Ouvrez rapport_credit.html dans votre navigateur.")
