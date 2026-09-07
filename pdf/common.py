import json
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


DARK_GREEN = colors.HexColor("#3A5A40")
MEDIUM_GREEN = colors.HexColor("#588157")
SAGE_GREEN = colors.HexColor("#A3B18A")
LIGHT_SAGE = colors.HexColor("#DCE4D2")

BEIGE = colors.HexColor("#F5F0E6")
LIGHT_BEIGE = colors.HexColor("#FAF7F2")
PAPER_BEIGE = colors.HexColor("#FFFDF7")

TEXT_DARK = colors.HexColor("#2F3E34")
TEXT_SOFT = colors.HexColor("#617064")

WHITE = colors.HexColor("#FFFFFF")
LIGHT_GRAY = colors.HexColor("#E9EDE8")
WARNING_BACKGROUND = colors.HexColor("#FFF3E6")
WARNING_BORDER = colors.HexColor("#D49A62")



def parse_json_data(json_text, fallback):
    if not json_text:
        return fallback

    try:
        return json.loads(json_text)

    except (json.JSONDecodeError, TypeError):
        return fallback


def safe_text(value, fallback="Nicht angegeben"):
    if value is None or value == "":
        return fallback

    return str(value)


def format_date(date_value):
    """
    Wandelt 2026-07-12 in 12.07.2026 um.
    """

    if not date_value:
        return "Nicht angegeben"

    parts = str(date_value).split("-")

    if len(parts) == 3:
        year, month, day = parts
        return f"{day}.{month}.{year}"

    return str(date_value)


def html_text(value):
    return escape(safe_text(value))


def split_lines(value):
    if not value:
        return []

    return [
        item.strip()
        for item in str(value).splitlines()
        if item.strip()
    ]


def create_styles():
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "Title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=DARK_GREEN,
            alignment=TA_CENTER,
            spaceAfter=8
        ),

        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=TEXT_SOFT,
            alignment=TA_CENTER,
            spaceAfter=10
        ),

        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=22,
            textColor=DARK_GREEN,
            spaceBefore=6,
            spaceAfter=12
        ),

        "category_title": ParagraphStyle(
            "CategoryTitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=DARK_GREEN,
            spaceAfter=5
        ),

        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=TEXT_DARK,
            alignment=TA_LEFT
        ),

        "body_center": ParagraphStyle(
            "BodyCenter",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=TEXT_DARK,
            alignment=TA_CENTER
        ),

        "small": ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=TEXT_SOFT
        ),

        "small_center": ParagraphStyle(
            "SmallCenter",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=TEXT_SOFT,
            alignment=TA_CENTER
        ),

        "table_header": ParagraphStyle(
            "TableHeader",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=WHITE,
            alignment=TA_CENTER
        ),

        "table_body": ParagraphStyle(
            "TableBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=TEXT_DARK,
            alignment=TA_LEFT
        ),

        "table_body_center": ParagraphStyle(
            "TableBodyCenter",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7,
            leading=9,
            textColor=TEXT_DARK,
            alignment=TA_CENTER
        ),

        "meal_name": ParagraphStyle(
            "MealName",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7,
            leading=9,
            textColor=DARK_GREEN,
            alignment=TA_LEFT,
            spaceAfter=3
        ),

        "medical_note": ParagraphStyle(
            "MedicalNote",
            parent=base["BodyText"],
            fontName="Helvetica-Oblique",
            fontSize=7,
            leading=10,
            textColor=TEXT_SOFT,
            alignment=TA_CENTER,
            spaceBefore=10
        ),

        "shopping_item": ParagraphStyle(
            "ShoppingItem",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=TEXT_DARK
        )
    }


def draw_portrait_page(canvas, document):
    canvas.saveState()

    width, height = A4

    canvas.setFillColor(BEIGE)
    canvas.rect(
        0,
        height - 20 * mm,
        width,
        20 * mm,
        fill=True,
        stroke=False
    )

    canvas.setFillColor(DARK_GREEN)
    canvas.setFont("Helvetica-Bold", 10)

    canvas.drawString(
        16 * mm,
        height - 13 * mm,
        "LOVE YOURSELF"
    )

    canvas.setStrokeColor(SAGE_GREEN)
    canvas.setLineWidth(0.5)

    canvas.line(
        16 * mm,
        15 * mm,
        width - 16 * mm,
        15 * mm
    )

    canvas.setFillColor(TEXT_SOFT)
    canvas.setFont("Helvetica", 7.5)

    canvas.drawRightString(
        width - 16 * mm,
        10 * mm,
        f"Seite {document.page}"
    )

    canvas.restoreState()


def draw_landscape_page(canvas, document):
    canvas.saveState()

    width, height = landscape(A4)

    canvas.setFillColor(BEIGE)
    canvas.rect(
        0,
        height - 18 * mm,
        width,
        18 * mm,
        fill=True,
        stroke=False
    )

    canvas.setFillColor(DARK_GREEN)
    canvas.setFont("Helvetica-Bold", 10)

    canvas.drawString(
        14 * mm,
        height - 12 * mm,
        "LOVE YOURSELF"
    )

    canvas.setStrokeColor(SAGE_GREEN)
    canvas.setLineWidth(0.5)

    canvas.line(
        14 * mm,
        13 * mm,
        width - 14 * mm,
        13 * mm
    )

    canvas.setFillColor(TEXT_SOFT)
    canvas.setFont("Helvetica", 7.5)

    canvas.drawRightString(
        width - 14 * mm,
        8 * mm,
        f"Seite {document.page}"
    )

    canvas.restoreState()


def draw_shopping_page(canvas, document):
    canvas.saveState()

    width, height = A4

    canvas.setFillColor(PAPER_BEIGE)
    canvas.rect(
        0,
        0,
        width,
        height,
        fill=True,
        stroke=False
    )

    # Dezente horizontale Papierlinien
    canvas.setStrokeColor(colors.HexColor("#E9E2D4"))
    canvas.setLineWidth(0.25)

    line_y = height - 35 * mm

    while line_y > 20 * mm:
        canvas.line(
            15 * mm,
            line_y,
            width - 15 * mm,
            line_y
        )

        line_y -= 9 * mm

    canvas.setFillColor(DARK_GREEN)
    canvas.setFont("Helvetica-Bold", 10)

    canvas.drawString(
        16 * mm,
        height - 15 * mm,
        "LOVE YOURSELF"
    )

    canvas.setFillColor(TEXT_SOFT)
    canvas.setFont("Helvetica", 7.5)

    canvas.drawRightString(
        width - 16 * mm,
        10 * mm,
        f"Seite {document.page}"
    )

    canvas.restoreState()


def build_plan_intro(
    title,
    user,
    plan,
    styles,
    show_calories=False
):
    elements = [
        Paragraph(
            html_text(title),
            styles["title"]
        ),

        Paragraph(
            (
                f"{html_text(user.username)} | "
                f"{format_date(plan.created_at)}"
            ),
            styles["subtitle"]
        ),

        Spacer(1, 3 * mm)
    ]

    summary_data = [
        [
            Paragraph(
                "<b>Name</b>",
                styles["body_center"]
            ),
            Paragraph(
                "<b>Datum</b>",
                styles["body_center"]
            ),
            Paragraph(
                "<b>Aktuelles Gewicht</b>",
                styles["body_center"]
            )
        ],
        [
            Paragraph(
                html_text(user.username),
                styles["body_center"]
            ),
            Paragraph(
                format_date(plan.created_at),
                styles["body_center"]
            ),
            Paragraph(
                (
                    f"{plan.current_weight} kg"
                    if plan.current_weight is not None
                    else "Nicht angegeben"
                ),
                styles["body_center"]
            )
        ]
    ]

    column_widths = [
        54 * mm,
        54 * mm,
        54 * mm
    ]

    if show_calories:
        summary_data[0].append(
            Paragraph(
                "<b>Kalorienziel</b>",
                styles["body_center"]
            )
        )

        summary_data[1].append(
            Paragraph(
                (
                    f"{plan.calories} kcal"
                    if plan.calories
                    else "Nicht berechnet"
                ),
                styles["body_center"]
            )
        )

        column_widths = [
            40 * mm,
            40 * mm,
            40 * mm,
            40 * mm
        ]

    summary_table = Table(
        summary_data,
        colWidths=column_widths,
        hAlign="CENTER"
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                LIGHT_SAGE
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                LIGHT_BEIGE
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.7,
                SAGE_GREEN
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                LIGHT_SAGE
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    elements.append(summary_table)
    elements.append(Spacer(1, 6 * mm))

    return elements


def build_safety_table(plan, styles):
    allergies = split_lines(
        plan.allergies_snapshot
    )

    excluded_foods = split_lines(
        plan.excluded_foods_snapshot
    )

    allergy_text = (
        "<br/>".join(
            f"- {escape(item)}"
            for item in allergies
        )
        if allergies
        else "Keine Allergien angegeben"
    )

    excluded_text = (
        "<br/>".join(
            f"- {escape(item)}"
            for item in excluded_foods
        )
        if excluded_foods
        else "Keine Lebensmittel ausgeschlossen"
    )

    data = [
        [
            Paragraph(
                "<b>Allergien</b>",
                styles["body"]
            ),
            Paragraph(
                "<b>Ausgeschlossene Lebensmittel</b>",
                styles["body"]
            )
        ],
        [
            Paragraph(
                allergy_text,
                styles["body"]
            ),
            Paragraph(
                excluded_text,
                styles["body"]
            )
        ]
    ]

    table = Table(
        data,
        colWidths=[
            80 * mm,
            80 * mm
        ],
        hAlign="CENTER"
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                WARNING_BACKGROUND
            ),
            (
                "BACKGROUND",
                (0, 1),
                (-1, 1),
                WHITE
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                WARNING_BORDER
            ),
            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.4,
                WARNING_BORDER
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            )
        ])
    )

    return table
