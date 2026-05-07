<?xml version="1.0" encoding="UTF-8"?>
<!--
  Fichier XSLT : rapport.xslt
  Rôle : Transformer le XML de résultats en rapport HTML lisible.
  La feuille de style XSL lit chaque nœud XML et produit du HTML formaté.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" encoding="UTF-8" indent="yes"/>

  <!-- ===== Template principal ===== -->
  <xsl:template match="/">
    <html lang="fr">
    <head>
      <meta charset="UTF-8"/>
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Rapport de Crédit</title>
      <style>
        /* ─── Style général ─── */
        body {
          font-family: 'Segoe UI', Arial, sans-serif;
          background: #f0f4f8;
          color: #333;
          margin: 0;
          padding: 20px;
        }
        .container {
          max-width: 860px;
          margin: auto;
          background: white;
          border-radius: 10px;
          box-shadow: 0 4px 15px rgba(0,0,0,0.1);
          padding: 35px 45px;
        }
        h1 {
          color: #1a3c6e;
          border-bottom: 3px solid #1a3c6e;
          padding-bottom: 10px;
        }
        h2 {
          color: #1a3c6e;
          margin-top: 30px;
          font-size: 1.1em;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        /* ─── Tableau de données ─── */
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 10px;
        }
        th {
          background: #1a3c6e;
          color: white;
          padding: 10px 14px;
          text-align: left;
        }
        td {
          padding: 9px 14px;
          border-bottom: 1px solid #e0e0e0;
        }
        tr:nth-child(even) td { background: #f7f9fc; }

        /* ─── Décision ─── */
        .decision-box {
          text-align: center;
          padding: 22px;
          border-radius: 8px;
          margin: 25px 0;
          font-size: 1.5em;
          font-weight: bold;
          letter-spacing: 2px;
        }
        .accepte  { background: #d4edda; color: #155724; border: 2px solid #28a745; }
        .refuse   { background: #f8d7da; color: #721c24; border: 2px solid #dc3545; }

        /* ─── Alerte surendettement ─── */
        .alerte {
          background: #fff3cd;
          border-left: 5px solid #ffc107;
          padding: 12px 18px;
          margin: 15px 0;
          border-radius: 4px;
        }

        /* ─── Graphique ─── */
        .chart-section { margin-top: 30px; }
        canvas { border: 1px solid #e0e0e0; border-radius: 8px; }

        footer {
          text-align: center;
          margin-top: 30px;
          color: #999;
          font-size: 0.85em;
        }
      </style>
    </head>
    <body>
    <div class="container">

      <h1>📋 Rapport de Simulation de Crédit</h1>

      <!-- ===== Section Emprunteur ===== -->
      <h2>👤 Informations de l'Emprunteur</h2>
      <table>
        <tr><th>Nom complet</th>
            <td><xsl:value-of select="rapport_credit/emprunteur/prenom"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="rapport_credit/emprunteur/nom"/>
            </td>
        </tr>
        <tr><th>Âge</th>
            <td><xsl:value-of select="rapport_credit/emprunteur/age"/> ans</td>
        </tr>
        <tr><th>Revenu mensuel</th>
            <td><xsl:value-of select="rapport_credit/emprunteur/revenu_mensuel"/> MAD</td>
        </tr>
      </table>

      <!-- ===== Section Prêt ===== -->
      <h2>🏦 Conditions du Prêt</h2>
      <table>
        <tr><th>Type de prêt</th>
            <td><xsl:value-of select="rapport_credit/pret/type"/></td>
        </tr>
        <tr><th>Montant emprunté</th>
            <td><xsl:value-of select="rapport_credit/pret/montant"/> MAD</td>
        </tr>
        <tr><th>Taux d'intérêt annuel</th>
            <td><xsl:value-of select="rapport_credit/pret/taux_annuel"/> %</td>
        </tr>
        <tr><th>Durée</th>
            <td><xsl:value-of select="rapport_credit/pret/duree_annees"/> ans</td>
        </tr>
      </table>

      <!-- ===== Section Résultats ===== -->
      <h2>📊 Résultats du Calcul</h2>
      <table>
        <tr><th>Mensualité</th>
            <td><strong><xsl:value-of select="rapport_credit/resultats/mensualite"/> MAD</strong></td>
        </tr>
        <tr><th>Coût total du crédit</th>
            <td><xsl:value-of select="rapport_credit/resultats/cout_total"/> MAD</td>
        </tr>
        <tr><th>Coût des intérêts</th>
            <td><xsl:value-of select="rapport_credit/resultats/cout_interets"/> MAD</td>
        </tr>
        <tr><th>Taux d'endettement</th>
            <td><xsl:value-of select="rapport_credit/resultats/taux_endettement"/> %</td>
        </tr>
      </table>

      <!-- ===== Alerte surendettement ===== -->
      <xsl:if test="rapport_credit/resultats/surendettement = 'true'">
        <div class="alerte">
          ⚠️ <strong>Attention :</strong> Le taux d'endettement dépasse 33 % du revenu mensuel.
          Risque de surendettement détecté.
        </div>
      </xsl:if>

      <!-- ===== Décision ===== -->
      <xsl:choose>
        <xsl:when test="rapport_credit/resultats/decision = 'Accepté'">
          <div class="decision-box accepte">✅ DEMANDE ACCEPTÉE</div>
        </xsl:when>
        <xsl:otherwise>
          <div class="decision-box refuse">❌ DEMANDE REFUSÉE</div>
        </xsl:otherwise>
      </xsl:choose>

      <!-- ===== Tableau d'amortissement ===== -->
      <h2>📅 Évolution du Capital Restant Dû (par année)</h2>
      <table>
        <tr>
          <th>Année</th>
          <th>Capital restant dû (MAD)</th>
        </tr>
        <!-- Ligne initiale (année 0 = montant complet) -->
        <tr>
          <td>0 (départ)</td>
          <td><xsl:value-of select="rapport_credit/pret/montant"/></td>
        </tr>
        <!-- Ligne pour chaque année -->
        <xsl:for-each select="rapport_credit/tableau_amortissement/ligne">
          <tr>
            <td><xsl:value-of select="annee"/></td>
            <td><xsl:value-of select="capital_restant"/></td>
          </tr>
        </xsl:for-each>
      </table>

      <!-- ===== Graphique (Chart.js via CDN) ===== -->
      <div class="chart-section">
        <h2>📈 Courbe du Capital Restant Dû</h2>
        <canvas id="graphique" width="760" height="300"></canvas>
      </div>

      <footer>Simulateur de Crédit — Projet académique ENSIAS IDF 2025-2026</footer>

    </div><!-- /container -->

    <!-- Script Chart.js : construit la courbe à partir des données XML extraites -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
      // Les données sont écrites directement dans le HTML par XSLT
      const labels  = [0, <xsl:for-each select="rapport_credit/tableau_amortissement/ligne"><xsl:value-of select="annee"/><xsl:if test="position() != last()">, </xsl:if></xsl:for-each>];
      const valeurs = [<xsl:value-of select="rapport_credit/pret/montant"/>, <xsl:for-each select="rapport_credit/tableau_amortissement/ligne"><xsl:value-of select="capital_restant"/><xsl:if test="position() != last()">, </xsl:if></xsl:for-each>];

      new Chart(document.getElementById('graphique'), {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Capital restant dû (MAD)',
            data: valeurs,
            borderColor: '#1a3c6e',
            backgroundColor: 'rgba(26, 60, 110, 0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 4
          }]
        },
        options: {
          responsive: false,
          plugins: { legend: { display: true } },
          scales: {
            x: { title: { display: true, text: 'Année' } },
            y: { title: { display: true, text: 'MAD' }, beginAtZero: true }
          }
        }
      });
    </script>

    </body>
    </html>
  </xsl:template>

</xsl:stylesheet>
