"""Génération PDF d'une prescription (spec 5.4).

Choix : reportlab (pur Python, portable Windows/Docker) + qrcode. weasyprint a été
écarté (dépendances système GTK/Pango/Cairo lourdes et fragiles).

Le PDF contient : identité du prescripteur (nom, établissement, RPPS), date,
la liste des outils avec consignes personnalisées + fiches résumées (avantages/limites),
et un QR code vers la version numérique interactive (lien partagé).
"""

import io

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import settings
from app.models.prescription import Prescription
from app.models.user import User

_PRIORITE_LABEL = {1: "Haute", 2: "Moyenne", 3: "Basse"}


def _qr_image(url: str) -> Image:
    qr = qrcode.make(url)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)
    return Image(buf, width=30 * mm, height=30 * mm)


def render_prescription_pdf(prescription: Prescription, ergo: User) -> bytes:
    """Retourne le PDF (bytes) de la prescription validée."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm, title="Prescription NeuroStep",
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=colors.HexColor("#1f8fc0"))
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8, textColor=colors.grey)
    body = styles["Normal"]
    elements: list = []

    # En-tête : titre + QR code (lien interactif) à droite.
    share_url = f"{settings.FRONTEND_URL}/p/{prescription.share_token}"
    header = Table(
        [[Paragraph("Prescription numérique", h1), _qr_image(share_url)]],
        colWidths=[None, 32 * mm],
    )
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elements.append(header)

    # Identité prescripteur.
    prescripteur = ergo.full_name or ergo.email
    lignes = [f"<b>Prescripteur :</b> {prescripteur}"]
    if ergo.etablissement:
        lignes.append(f"<b>Établissement :</b> {ergo.etablissement}")
    if ergo.rpps:
        verif = " (vérifié)" if ergo.rpps_verified else ""
        lignes.append(f"<b>RPPS :</b> {ergo.rpps}{verif}")
    date = (prescription.validated_at or prescription.created_at).strftime("%d/%m/%Y")
    lignes.append(f"<b>Date :</b> {date}")
    elements.append(Spacer(1, 6))
    for ligne in lignes:
        elements.append(Paragraph(ligne, body))

    if prescription.notes:
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f"<b>Notes :</b> {prescription.notes}", body))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Outils recommandés", styles["Heading2"]))

    for idx, item in enumerate(prescription.items, start=1):
        app = item.application
        elements.append(Spacer(1, 8))
        prio = _PRIORITE_LABEL.get(item.priorite, str(item.priorite))
        elements.append(
            Paragraph(f"{idx}. <b>{app.nom}</b> — priorité {prio}", styles["Heading3"])
        )
        meta = f"{', '.join(app.plateformes or []) or '—'} · {'Gratuit' if app.gratuit else 'Payant'}"
        elements.append(Paragraph(meta, small))
        if item.consignes:
            elements.append(Paragraph(f"<b>Consignes :</b> {item.consignes}", body))
        if app.description:
            # Fiche résumée (avantages / limites) telle que stockée.
            elements.append(Paragraph(app.description.replace("\n", "<br/>"), body))

    elements.append(Spacer(1, 18))
    elements.append(
        Paragraph(
            "Document généré par NeuroStep. Scannez le QR code pour la version "
            "interactive et fournir un retour d'usage.",
            small,
        )
    )

    doc.build(elements)
    return buf.getvalue()
