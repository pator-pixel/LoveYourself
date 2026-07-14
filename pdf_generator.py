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
    TableStyle
)


# ============================================================
# Farben
# ============================================================

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


# ============================================================
# Allgemeine Hilfsfunktionen
# ============================================================

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


# ============================================================
# Kopf- und Fußzeilen
# ============================================================

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


# ============================================================
# Gemeinsame Kopfbereiche
# ============================================================

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


# ============================================================
# Ernährungsplan-PDF
# ============================================================

def create_meal_cell(meal, styles):
    meal_name = safe_text(
        meal.get("name")
    )

    calories = safe_text(
        meal.get("calories"),
        "0"
    )

    return [
        Paragraph(
            escape(meal_name),
            styles["meal_name"]
        ),
        Paragraph(
            f"ca. {escape(calories)} kcal",
            styles["small"]
        )
    ]


def generate_nutrition_pdf(
    plan,
    user,
    profile,
    file_path
):
    nutrition_days = parse_json_data(
        plan.nutrition_data,
        []
    )

    document = SimpleDocTemplate(
        file_path,
        pagesize=landscape(A4),
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
        title=plan.nutrition_title,
        author="Love Yourself"
    )

    styles = create_styles()
    story = []

    story.extend(
        build_plan_intro(
            title=plan.nutrition_title,
            user=user,
            plan=plan,
            styles=styles,
            show_calories=True
        )
    )

    story.append(
        build_safety_table(
            plan,
            styles
        )
    )

    story.append(Spacer(1, 6 * mm))

    table_data = [
        [
            Paragraph(
                "Tag",
                styles["table_header"]
            ),
            Paragraph(
                "Frühstück",
                styles["table_header"]
            ),
            Paragraph(
                "Mittagessen",
                styles["table_header"]
            ),
            Paragraph(
                "Abendessen",
                styles["table_header"]
            ),
            Paragraph(
                "Snack",
                styles["table_header"]
            )
        ]
    ]

    for nutrition_day in nutrition_days:
        table_data.append([
            Paragraph(
                f"<b>Tag {nutrition_day.get('day', '')}</b>",
                styles["table_body_center"]
            ),
            create_meal_cell(
                nutrition_day.get(
                    "breakfast",
                    {}
                ),
                styles
            ),
            create_meal_cell(
                nutrition_day.get(
                    "lunch",
                    {}
                ),
                styles
            ),
            create_meal_cell(
                nutrition_day.get(
                    "dinner",
                    {}
                ),
                styles
            ),
            create_meal_cell(
                nutrition_day.get(
                    "snack",
                    {}
                ),
                styles
            )
        ])

    nutrition_table = Table(
        table_data,
        colWidths=[
            23 * mm,
            56 * mm,
            56 * mm,
            56 * mm,
            56 * mm
        ],
        repeatRows=1,
        hAlign="CENTER"
    )

    nutrition_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                DARK_GREEN
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                WHITE
            ),
            (
                "BACKGROUND",
                (0, 1),
                (0, -1),
                LIGHT_SAGE
            ),
            (
                "ROWBACKGROUNDS",
                (1, 1),
                (-1, -1),
                [
                    WHITE,
                    LIGHT_BEIGE
                ]
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
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
                "TOP"
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                6
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

    story.append(nutrition_table)

    story.append(
        Paragraph(
            (
                "Bei gesundheitlichen Einschränkungen bitte "
                "ärztlich abklären. Der Plan ersetzt keine "
                "medizinische Beratung."
            ),
            styles["medical_note"]
        )
    )

    document.build(
        story,
        onFirstPage=draw_landscape_page,
        onLaterPages=draw_landscape_page
    )


# ============================================================
# Fitnessplan-PDF
# ============================================================

def generate_fitness_pdf(
    plan,
    user,
    profile,
    file_path
):
    fitness_days = parse_json_data(
        plan.fitness_data,
        []
    )

    document = SimpleDocTemplate(
        file_path,
        pagesize=landscape(A4),
        leftMargin=13 * mm,
        rightMargin=13 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
        title=plan.fitness_title,
        author="Love Yourself"
    )

    styles = create_styles()
    story = []

    story.extend(
        build_plan_intro(
            title=plan.fitness_title,
            user=user,
            plan=plan,
            styles=styles,
            show_calories=False
        )
    )

    for index, fitness_day in enumerate(
        fitness_days
    ):
        day_number = fitness_day.get(
            "day",
            index + 1
        )

        story.append(
            Paragraph(
                f"Tag {day_number}",
                styles["section_title"]
            )
        )

        exercise_data = [
            [
                Paragraph(
                    "Übung",
                    styles["table_header"]
                ),
                Paragraph(
                    "Sätze",
                    styles["table_header"]
                ),
                Paragraph(
                    "Wiederholungen / Dauer",
                    styles["table_header"]
                ),
                Paragraph(
                    "Pause",
                    styles["table_header"]
                ),
                Paragraph(
                    "Einfache Alternative",
                    styles["table_header"]
                )
            ]
        ]

        exercises = fitness_day.get(
            "exercises",
            []
        )

        for exercise in exercises:
            exercise_data.append([
                Paragraph(
                    f"<b>{escape(safe_text(exercise.get('name')))}</b>",
                    styles["table_body"]
                ),
                Paragraph(
                    escape(
                        safe_text(
                            exercise.get("sets")
                        )
                    ),
                    styles["table_body_center"]
                ),
                Paragraph(
                    escape(
                        safe_text(
                            exercise.get(
                                "repetitions"
                            )
                        )
                    ),
                    styles["table_body_center"]
                ),
                Paragraph(
                    escape(
                        safe_text(
                            exercise.get("pause")
                        )
                    ),
                    styles["table_body_center"]
                ),
                Paragraph(
                    escape(
                        safe_text(
                            exercise.get(
                                "alternative"
                            )
                        )
                    ),
                    styles["table_body"]
                )
            ])

        exercise_table = Table(
            exercise_data,
            colWidths=[
                55 * mm,
                26 * mm,
                50 * mm,
                31 * mm,
                82 * mm
            ],
            repeatRows=1,
            hAlign="CENTER"
        )

        exercise_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    DARK_GREEN
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        WHITE,
                        LIGHT_BEIGE
                    ]
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
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
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6
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

        steps_text = safe_text(
            fitness_day.get(
                "steps_alternative"
            )
        )

        steps_box = Table(
            [
                [
                    Paragraph(
                        "<b>Keine Zeit für das Training?</b>",
                        styles["body"]
                    ),
                    Paragraph(
                        escape(steps_text),
                        styles["body"]
                    )
                ]
            ],
            colWidths=[
                66 * mm,
                178 * mm
            ],
            hAlign="CENTER"
        )

        steps_box.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    BEIGE
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    SAGE_GREEN
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
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

        story.append(exercise_table)
        story.append(Spacer(1, 3 * mm))
        story.append(steps_box)

        if index < len(fitness_days) - 1:
            story.append(Spacer(1, 6 * mm))

    story.append(
        Paragraph(
            (
                "Bei gesundheitlichen Einschränkungen bitte "
                "ärztlich abklären. Der Plan ersetzt keine "
                "medizinische Beratung."
            ),
            styles["medical_note"]
        )
    )

    document.build(
        story,
        onFirstPage=draw_landscape_page,
        onLaterPages=draw_landscape_page
    )


# ============================================================
# Einkaufsliste-PDF
# ============================================================

def build_shopping_category_box(
    category,
    styles
):
    category_name = safe_text(
        category.get("category"),
        "Sonstiges"
    )

    items = category.get(
        "items",
        []
    )

    content = [
        Paragraph(
            escape(category_name),
            styles["category_title"]
        )
    ]

    if not items:
        content.append(
            Paragraph(
                "Keine Einträge",
                styles["small"]
            )
        )

    for item in items:
        item_table = Table(
            [
                [
                    "",
                    Paragraph(
                        escape(safe_text(item)),
                        styles["shopping_item"]
                    )
                ]
            ],
            colWidths=[
                8 * mm,
                66 * mm
            ]
        )

        item_table.setStyle(
            TableStyle([
                (
                    "BOX",
                    (0, 0),
                    (0, 0),
                    0.8,
                    DARK_GREEN
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, 0),
                    WHITE
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                )
            ])
        )

        content.append(item_table)
        content.append(Spacer(1, 1.5 * mm))

    category_box = Table(
        [[content]],
        colWidths=[82 * mm]
    )

    category_box.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.Color(
                    1,
                    1,
                    1,
                    alpha=0.90
                )
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                SAGE_GREEN
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                9
            )
        ])
    )

    return category_box


def generate_shopping_pdf(
    plan,
    user,
    profile,
    file_path
):
    shopping_categories = parse_json_data(
        plan.shopping_data,
        []
    )

    document = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=27 * mm,
        bottomMargin=18 * mm,
        title=plan.shopping_title,
        author="Love Yourself"
    )

    styles = create_styles()
    story = []

    story.append(
        Paragraph(
            html_text(plan.shopping_title),
            styles["title"]
        )
    )

    story.append(
        Paragraph(
            (
                f"Für {html_text(user.username)} | "
                f"{format_date(plan.created_at)}"
            ),
            styles["subtitle"]
        )
    )

    story.append(Spacer(1, 3 * mm))

    note_table = Table(
        [
            [
                Paragraph(
                    (
                        "<b>Deine Einkaufsliste</b><br/>"
                        "Hake die Zutaten beim Einkaufen einfach ab."
                    ),
                    styles["body_center"]
                )
            ]
        ],
        colWidths=[160 * mm]
    )

    note_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                LIGHT_SAGE
            ),
            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                SAGE_GREEN
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                9
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                9
            )
        ])
    )

    story.append(note_table)
    story.append(Spacer(1, 7 * mm))

    category_boxes = [
        build_shopping_category_box(
            category,
            styles
        )
        for category in shopping_categories
    ]

    rows = []

    for index in range(
        0,
        len(category_boxes),
        2
    ):
        first_box = category_boxes[index]

        second_box = (
            category_boxes[index + 1]
            if index + 1 < len(category_boxes)
            else ""
        )

        rows.append([
            first_box,
            second_box
        ])

    if not rows:
        rows = [
            [
                Paragraph(
                    "Keine Einkaufsliste vorhanden.",
                    styles["body_center"]
                ),
                ""
            ]
        ]

    shopping_grid = Table(
        rows,
        colWidths=[
            84 * mm,
            84 * mm
        ],
        hAlign="CENTER"
    )

    shopping_grid.setStyle(
        TableStyle([
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
                3
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                3
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                3
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3
            )
        ])
    )

    story.append(shopping_grid)

    document.build(
        story,
        onFirstPage=draw_shopping_page,
        onLaterPages=draw_shopping_page
    )