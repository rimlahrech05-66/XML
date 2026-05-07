"""
simulateur.py
=============
Script principal du Simulateur de Crédit.

Étapes :
  1. Valide le XML avec le XSD
  2. Lit les données du XML
  3. Calcule les mensualités, coût total, capital restant dû
  4. Détecte un cas de surendettement
  5. Génère un fichier XML enrichi (résultats) pour la transformation XSLT
"""

import xml.etree.ElementTree as ET
from lxml import etree
import math


# ─────────────────────────────────────────────
#  1. VALIDATION XML / XSD
# ─────────────────────────────────────────────

def valider_xml(fichier_xml, fichier_xsd):
    """Valide le fichier XML contre le schéma XSD. Lève une erreur si invalide."""
    with open(fichier_xsd, "rb") as f:
        schema_doc = etree.parse(f)
    schema = etree.XMLSchema(schema_doc)

    with open(fichier_xml, "rb") as f:
        doc = etree.parse(f)

    if schema.validate(doc):
        print("[OK] XML valide selon le XSD.")
    else:
        # Affiche les erreurs de validation et arrête le programme
        for erreur in schema.error_log:
            print(f"[ERREUR] {erreur.message}")
        raise SystemExit("Validation échouée. Corrigez le XML avant de continuer.")


# ─────────────────────────────────────────────
#  2. LECTURE DES DONNÉES XML
# ─────────────────────────────────────────────

def lire_donnees(fichier_xml):
    """Lit et retourne les données du XML sous forme de dictionnaire."""
    tree = ET.parse(fichier_xml)
    root = tree.getroot()

    donnees = {
        "nom":            root.findtext("emprunteur/nom"),
        "prenom":         root.findtext("emprunteur/prenom"),
        "age":            int(root.findtext("emprunteur/age")),
        "revenu_mensuel": float(root.findtext("emprunteur/revenu_mensuel")),
        "montant":        float(root.findtext("pret/montant")),
        "taux_annuel":    float(root.findtext("pret/taux_annuel")),
        "duree_annees":   int(root.findtext("pret/duree_annees")),
        "type_pret":      root.findtext("pret/type"),
    }
    return donnees


# ─────────────────────────────────────────────
#  3. CALCULS FINANCIERS
# ─────────────────────────────────────────────

def calculer_mensualite(montant, taux_annuel, duree_annees):
    """
    Calcule la mensualité constante (amortissement français).

    Formule : M = C * r / (1 - (1 + r)^(-n))
      - C : capital emprunté
      - r : taux mensuel = taux_annuel / 12 / 100
      - n : nombre de mensualités = duree_annees * 12
    """
    r = taux_annuel / 12 / 100   # taux mensuel
    n = duree_annees * 12        # nombre total de mensualités

    if r == 0:
        return montant / n       # cas sans intérêt

    mensualite = montant * r / (1 - (1 + r) ** (-n))
    return round(mensualite, 2)


def calculer_cout_total(mensualite, duree_annees):
    """Coût total = somme de toutes les mensualités."""
    return round(mensualite * duree_annees * 12, 2)


def calculer_cout_interets(cout_total, montant):
    """Coût des intérêts = coût total - capital emprunté."""
    return round(cout_total - montant, 2)


def calculer_tableau_amortissement(montant, taux_annuel, duree_annees, mensualite):
    """
    Génère le tableau d'amortissement mois par mois.
    Retourne une liste de dicts avec : mois, capital_restant, interet, amortissement.
    """
    r = taux_annuel / 12 / 100
    capital = montant
    tableau = []

    for mois in range(1, duree_annees * 12 + 1):
        interet      = round(capital * r, 2)
        amortissement = round(mensualite - interet, 2)
        capital       = round(capital - amortissement, 2)

        # Correction d'arrondi au dernier mois
        if capital < 0:
            capital = 0.0

        tableau.append({
            "mois":          mois,
            "capital_restant": capital,
            "interet":        interet,
            "amortissement":  amortissement,
        })

    return tableau


# ─────────────────────────────────────────────
#  4. DÉTECTION DU SURENDETTEMENT
# ─────────────────────────────────────────────

def detecter_surendettement(mensualite, revenu_mensuel):
    """
    Règle simple : le taux d'endettement ne doit pas dépasser 33 % du revenu.
    Retourne (taux_endettement, est_surendetté).
    """
    taux = (mensualite / revenu_mensuel) * 100
    return round(taux, 2), taux > 33


# ─────────────────────────────────────────────
#  5. GÉNÉRATION DU XML ENRICHI (pour XSLT)
# ─────────────────────────────────────────────

def generer_xml_resultats(donnees, resultats, tableau, fichier_sortie):
    """Écrit un XML contenant toutes les données + résultats calculés."""

    root = ET.Element("rapport_credit")

    # Bloc emprunteur
    emp = ET.SubElement(root, "emprunteur")
    ET.SubElement(emp, "nom").text           = donnees["nom"]
    ET.SubElement(emp, "prenom").text        = donnees["prenom"]
    ET.SubElement(emp, "age").text           = str(donnees["age"])
    ET.SubElement(emp, "revenu_mensuel").text = str(donnees["revenu_mensuel"])

    # Bloc prêt
    pret = ET.SubElement(root, "pret")
    ET.SubElement(pret, "montant").text       = str(donnees["montant"])
    ET.SubElement(pret, "taux_annuel").text   = str(donnees["taux_annuel"])
    ET.SubElement(pret, "duree_annees").text  = str(donnees["duree_annees"])
    ET.SubElement(pret, "type").text          = donnees["type_pret"]

    # Bloc résultats
    res = ET.SubElement(root, "resultats")
    ET.SubElement(res, "mensualite").text        = str(resultats["mensualite"])
    ET.SubElement(res, "cout_total").text         = str(resultats["cout_total"])
    ET.SubElement(res, "cout_interets").text      = str(resultats["cout_interets"])
    ET.SubElement(res, "taux_endettement").text   = str(resultats["taux_endettement"])
    ET.SubElement(res, "surendettement").text     = str(resultats["surendettement"]).lower()
    ET.SubElement(res, "decision").text           = resultats["decision"]

    # Tableau d'amortissement (uniquement annuel pour alléger le XML)
    tab = ET.SubElement(root, "tableau_amortissement")
    for ligne in tableau:
        if ligne["mois"] % 12 == 0:  # Une ligne par an
            annee = ligne["mois"] // 12
            l = ET.SubElement(tab, "ligne")
            ET.SubElement(l, "annee").text           = str(annee)
            ET.SubElement(l, "capital_restant").text = str(ligne["capital_restant"])

    # Écriture du fichier
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(fichier_sortie, encoding="utf-8", xml_declaration=True)
    print(f"[OK] Fichier résultats XML généré : {fichier_sortie}")


# ─────────────────────────────────────────────
#  PROGRAMME PRINCIPAL
# ─────────────────────────────────────────────

if __name__ == "__main__":

    FICHIER_XML     = "demande_credit.xml"
    FICHIER_XSD     = "demande_credit.xsd"
    FICHIER_RESULTATS = "resultats_credit.xml"

    # Étape 1 : Validation
    valider_xml(FICHIER_XML, FICHIER_XSD)

    # Étape 2 : Lecture
    donnees = lire_donnees(FICHIER_XML)
    print(f"\nDemande de : {donnees['prenom']} {donnees['nom']}")
    print(f"Prêt : {donnees['montant']} MAD sur {donnees['duree_annees']} ans à {donnees['taux_annuel']}%")

    # Étape 3 : Calculs
    mensualite    = calculer_mensualite(donnees["montant"], donnees["taux_annuel"], donnees["duree_annees"])
    cout_total    = calculer_cout_total(mensualite, donnees["duree_annees"])
    cout_interets = calculer_cout_interets(cout_total, donnees["montant"])
    tableau       = calculer_tableau_amortissement(donnees["montant"], donnees["taux_annuel"],
                                                   donnees["duree_annees"], mensualite)

    print(f"\nMensualité      : {mensualite} MAD")
    print(f"Coût total      : {cout_total} MAD")
    print(f"Coût des intérêts : {cout_interets} MAD")

    # Étape 4 : Surendettement
    taux_endettement, surendettte = detecter_surendettement(mensualite, donnees["revenu_mensuel"])
    decision = "Refusé" if surendettte else "Accepté"
    print(f"\nTaux d'endettement : {taux_endettement}% {'⚠ SURENDETTEMENT' if surendettte else '✓ OK'}")
    print(f"Décision : {decision}")

    resultats = {
        "mensualite":       mensualite,
        "cout_total":       cout_total,
        "cout_interets":    cout_interets,
        "taux_endettement": taux_endettement,
        "surendettement":   surendettte,
        "decision":         decision,
    }

    # Étape 5 : Génération du XML enrichi
    generer_xml_resultats(donnees, resultats, tableau, FICHIER_RESULTATS)
    print("\n[INFO] Lancez ensuite : python appliquer_xslt.py")
