from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


DARK_GREEN = colors.HexColor("#3A5A40")
SAGE_GREEN = colors.HexColor("#A3B18A")
BEIGE = colors.HexColor("#F5F0E6")
TEXT_DARK = colors.HexColor("#2F3E34")


def generate_plan_pdf(plan, user, profile, file_path):
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        textColor=DARK_GREEN,
        fontSize=26,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        textColor=DARK_GREEN,
        fontSize=16,
        spaceBefore=18,
        spaceAfter=10
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        textColor=TEXT_DARK,
        fontSize=10,
        leading=15
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        textColor=TEXT_DARK,
        fontSize=9,
        leading=13
    )

    story = []

    story.append(Paragraph("Love Yourself", title_style))
    story.append(Paragraph("Dein persönlicher Gesundheits- und Fitnessplan", normal_style))
    story.append(Spacer(1, 20))

    user_data = [
        ["Benutzer", user.username],
        ["Erstellt am", plan.created_at],
        ["Kalorienziel", f"{plan.calories} kcal" if plan.calories else "Nicht berechnet"],
        ["Aktuelles Gewicht", f"{profile.weight} kg" if profile and profile.weight else "Nicht angegeben"],
        ["Zielgewicht", f"{profile.goal_weight} kg" if profile and profile.goal_weight else "Nicht angegeben"],
        ["Ernährungsform", profile.diet_type if profile and profile.diet_type else "Nicht angegeben"],
        ["Fitnesslevel", profile.fitness_level if profile and profile.fitness_level else "Nicht angegeben"],
    ]

    table = Table(user_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BEIGE),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_DARK),
        ("BOX", (0, 0), (-1, -1), 1, SAGE_GREEN),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, SAGE_GREEN),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    story.append(Paragraph("AI Prompt / Planinhalt", heading_style))

    if plan.generated_text:
        text = plan.generated_text.replace("\n", "<br/>")
    else:
        text = plan.prompt.replace("\n", "<br/>")

    story.append(Paragraph(text, normal_style))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Hinweis", heading_style))
    story.append(Paragraph(
        "Bei gesundheitlichen Einschränkungen bitte ärztlich abklären.",
        small_style
    ))

    doc.build(story)