from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import (
    TA_CENTER,
    TA_LEFT,
)
from reportlab.lib.pagesizes import (
    A4,
    landscape,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    Image,
    KeepInFrame,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from pdf.common import (
    DARK_GREEN,
    TEXT_DARK,
    TEXT_SOFT,
    WHITE,
    create_styles,
    parse_json_data,
    safe_text,
    split_lines,
)


# ============================================================
# FARBEN
# ============================================================

VERY_LIGHT_SAGE = colors.HexColor(
    "#F3F6F1"
)

LINE_COLOR = colors.HexColor(
    "#D6DDD3"
)

FOOTER_LINE = colors.HexColor(
    "#DADFD8"
)

ROUNDED_BORDER = colors.HexColor(
    "#AEBBA9"
)


# ============================================================
# LOGO
# ============================================================

def get_logo_path():
    """
    Liefert den absoluten Pfad zum Love Yourself Logo.
    """

    project_root = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    return (
        project_root
        / "static"
        / "images"
        / "logo.png"
    )


# ============================================================
# ABGERUNDETER TABELLENRAHMEN
# ============================================================

class RoundedTableBox(Flowable):
    """
    Zeichnet eine Tabelle mit echten,
    vollständig sichtbaren abgerundeten Außenkanten.

    Die Tabelle wird zuerst auf die runde Form beschnitten.
    Danach wird der Außenrahmen noch einmal darüber gezeichnet.
    """

    def __init__(
        self,
        table,
        radius=2.8 * mm,
        border_color=ROUNDED_BORDER,
        border_width=0.8,
    ):
        super().__init__()

        self.table = table

        self.radius = radius
        self.border_color = border_color
        self.border_width = border_width

        self.table_width = 0
        self.table_height = 0


    def wrap(
        self,
        availWidth,
        availHeight
    ):
        (
            self.table_width,
            self.table_height
        ) = self.table.wrap(
            availWidth,
            availHeight
        )

        return (
            self.table_width,
            self.table_height
        )


    def draw(self):
        canvas = self.canv


        # =====================================================
        # TABELLE AUF ABGERUNDETE FORM BESCHNEIDEN
        # =====================================================

        canvas.saveState()


        clip_path = canvas.beginPath()

        clip_path.roundRect(
            0,
            0,
            self.table_width,
            self.table_height,
            self.radius
        )


        canvas.clipPath(
            clip_path,
            stroke=0,
            fill=0
        )


        self.table.drawOn(
            canvas,
            0,
            0
        )


        canvas.restoreState()


        # =====================================================
        # SAUBEREN AUSSENRAHMEN DARÜBER ZEICHNEN
        # =====================================================

        canvas.saveState()


        canvas.setStrokeColor(
            self.border_color
        )

        canvas.setLineWidth(
            self.border_width
        )


        canvas.roundRect(
            0,
            0,
            self.table_width,
            self.table_height,
            self.radius,
            stroke=1,
            fill=0
        )


        canvas.restoreState()


# ============================================================
# STYLES
# ============================================================

def create_nutrition_styles():
    """
    Ergänzt die allgemeinen PDF-Styles
    um kompakte Ernährungsplan-Styles.
    """

    styles = create_styles()


    styles["nutrition_title"] = ParagraphStyle(
        "NutritionTitle",
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
        spaceAfter=0,
    )


    styles["day_title"] = ParagraphStyle(
        "NutritionDayTitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
        spaceAfter=2 * mm,
    )


    styles["meal_column_header"] = ParagraphStyle(
        "MealColumnHeader",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=DARK_GREEN,
        alignment=TA_CENTER,
    )


    styles["recipe_name"] = ParagraphStyle(
        "RecipeName",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
        spaceAfter=1.5,
    )


    styles["recipe_calories"] = ParagraphStyle(
        "RecipeCalories",
        fontName="Helvetica",
        fontSize=6.2,
        leading=7.5,
        textColor=TEXT_SOFT,
        alignment=TA_LEFT,
        spaceAfter=2.5,
    )


    styles["recipe_heading"] = ParagraphStyle(
        "RecipeHeading",
        fontName="Helvetica-Bold",
        fontSize=6.3,
        leading=7.5,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        spaceBefore=1,
        spaceAfter=1.5,
    )


    styles["recipe_text"] = ParagraphStyle(
        "RecipeText",
        fontName="Helvetica",
        fontSize=5.8,
        leading=6.8,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        spaceAfter=1,
    )


    styles["footer_label"] = ParagraphStyle(
        "NutritionFooterLabel",
        fontName="Helvetica-Bold",
        fontSize=5.7,
        leading=6.5,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
    )


    styles["footer_text"] = ParagraphStyle(
        "NutritionFooterText",
        fontName="Helvetica",
        fontSize=5.5,
        leading=6.4,
        textColor=TEXT_SOFT,
        alignment=TA_LEFT,
    )


    return styles


# ============================================================
# LISTEN BEREINIGEN
# ============================================================

def _clean_list(values):
    """
    Bereinigt Zutaten oder Zubereitungsschritte.
    """

    if not values:
        return []

    if isinstance(
        values,
        str
    ):
        return [
            item.strip()
            for item in values.splitlines()
            if item.strip()
        ]

    return [
        str(item).strip()
        for item in values
        if str(item).strip()
    ]


# ============================================================
# REZEPT-ZELLE
# ============================================================

def create_recipe_cell(
    meal,
    styles
):
    """
    Erstellt eine sichtbare Rezeptzelle mit:
    - Gerichtname
    - Kalorien
    - Zutaten
    - Zubereitung
    """

    meal = meal or {}


    meal_name = safe_text(
        meal.get("name"),
        "Nicht angegeben"
    )


    calories = safe_text(
        meal.get("calories"),
        "0"
    )


    ingredients = _clean_list(
        meal.get(
            "ingredients",
            []
        )
    )


    preparation = _clean_list(
        meal.get(
            "preparation",
            []
        )
    )


    content = []


    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    content.append(
        Paragraph(
            escape(meal_name),
            styles["recipe_name"]
        )
    )


    # --------------------------------------------------------
    # KALORIEN
    # --------------------------------------------------------

    content.append(
        Paragraph(
            f"ca. {escape(calories)} kcal",
            styles["recipe_calories"]
        )
    )


    # --------------------------------------------------------
    # ZUTATEN
    # --------------------------------------------------------

    content.append(
        Paragraph(
            "Zutaten",
            styles["recipe_heading"]
        )
    )


    if ingredients:

        for ingredient in ingredients:

            content.append(
                Paragraph(
                    f"- {escape(ingredient)}",
                    styles["recipe_text"]
                )
            )

    else:

        content.append(
            Paragraph(
                "Keine Zutaten gespeichert.",
                styles["recipe_text"]
            )
        )


    # --------------------------------------------------------
    # ZUBEREITUNG
    # --------------------------------------------------------

    content.append(
        Spacer(
            1,
            0.8 * mm
        )
    )


    content.append(
        Paragraph(
            "Zubereitung",
            styles["recipe_heading"]
        )
    )


    if preparation:

        for number, step in enumerate(
            preparation,
            start=1
        ):

            content.append(
                Paragraph(
                    (
                        f"{number}. "
                        f"{escape(step)}"
                    ),
                    styles["recipe_text"]
                )
            )

    else:

        content.append(
            Paragraph(
                "Keine Zubereitung gespeichert.",
                styles["recipe_text"]
            )
        )


    # --------------------------------------------------------
    # INHALT INNERHALB DER ZELLE HALTEN
    # --------------------------------------------------------

    return KeepInFrame(
        maxWidth=61 * mm,
        maxHeight=82 * mm,
        content=content,
        mode="shrink",
        hAlign="LEFT",
        vAlign="TOP",
    )


# ============================================================
# KOPFZEILE MIT LOGO
# ============================================================

def build_page_header(
    styles
):
    """
    Erstellt Logo + Überschrift Ernährungsplan.
    """

    logo_path = get_logo_path()


    if logo_path.is_file():

        logo = Image(
            str(logo_path),
            width=17 * mm,
            height=17 * mm,
        )

    else:

        logo = ""


    title = Paragraph(
        "Ernährungsplan",
        styles["nutrition_title"]
    )


    header_table = Table(
        [
            [
                logo,
                title
            ]
        ],
        colWidths=[
            22 * mm,
            226 * mm
        ],
    )


    header_table.setStyle(
        TableStyle([
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
                0
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                0
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                0
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                0
            ),
        ])
    )


    return header_table


# ============================================================
# EINEN TAG BAUEN
# ============================================================

def build_nutrition_day(
    nutrition_day,
    styles
):
    """
    Baut einen kompletten Ernährungstag.

    Reihenfolge:
    Frühstück
    Mittagessen
    Snack
    Abendessen
    """

    day_number = safe_text(
        nutrition_day.get(
            "day"
        ),
        ""
    )


    day_title = Paragraph(
        f"Tag {escape(day_number)}",
        styles["day_title"]
    )


    table_data = [
        [
            Paragraph(
                "Frühstück",
                styles[
                    "meal_column_header"
                ]
            ),

            Paragraph(
                "Mittagessen",
                styles[
                    "meal_column_header"
                ]
            ),

            Paragraph(
                "Snack",
                styles[
                    "meal_column_header"
                ]
            ),

            Paragraph(
                "Abendessen",
                styles[
                    "meal_column_header"
                ]
            ),
        ],

        [
            create_recipe_cell(
                nutrition_day.get(
                    "breakfast",
                    {}
                ),
                styles
            ),

            create_recipe_cell(
                nutrition_day.get(
                    "lunch",
                    {}
                ),
                styles
            ),

            create_recipe_cell(
                nutrition_day.get(
                    "snack",
                    {}
                ),
                styles
            ),

            create_recipe_cell(
                nutrition_day.get(
                    "dinner",
                    {}
                ),
                styles
            ),
        ]
    ]


    nutrition_table = Table(
        table_data,
        colWidths=[
            64 * mm,
            64 * mm,
            64 * mm,
            64 * mm,
        ],
        hAlign="CENTER",
    )


    nutrition_table.setStyle(
        TableStyle([

            # ------------------------------------------------
            # KOPF
            # ------------------------------------------------

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                VERY_LIGHT_SAGE
            ),

            # ------------------------------------------------
            # INHALT BLEIBT WEISS
            # ------------------------------------------------

            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                WHITE
            ),

            # ------------------------------------------------
            # NUR INNERE LINIEN
            # Außenrahmen übernimmt RoundedTableBox
            # ------------------------------------------------

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.35,
                LINE_COLOR
            ),

            # ------------------------------------------------
            # AUSRICHTUNG
            # ------------------------------------------------

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            # ------------------------------------------------
            # KOPF-ABSTÄNDE
            # ------------------------------------------------

            (
                "LEFTPADDING",
                (0, 0),
                (-1, 0),
                4
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, 0),
                4
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, 0),
                4
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                4
            ),

            # ------------------------------------------------
            # REZEPT-ABSTÄNDE
            # ------------------------------------------------

            (
                "LEFTPADDING",
                (0, 1),
                (-1, -1),
                5
            ),

            (
                "RIGHTPADDING",
                (0, 1),
                (-1, -1),
                5
            ),

            (
                "TOPPADDING",
                (0, 1),
                (-1, -1),
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 1),
                (-1, -1),
                5
            ),
        ])
    )


    rounded_table = RoundedTableBox(
        nutrition_table,
        radius=2.8 * mm,
        border_color=ROUNDED_BORDER,
        border_width=0.8,
    )


    return KeepTogether([
        day_title,
        rounded_table,
    ])


# ============================================================
# FUSSZEILE
# ============================================================

def draw_nutrition_footer(
    canvas,
    document,
    plan,
    styles
):
    """
    Kompakte Fußzeile:
    - Kalorienziel
    - Allergien
    - unerwünschte Lebensmittel
    """

    canvas.saveState()


    page_width, _ = landscape(
        A4
    )


    # --------------------------------------------------------
    # TRENNLINIE
    # --------------------------------------------------------

    canvas.setStrokeColor(
        FOOTER_LINE
    )

    canvas.setLineWidth(
        0.4
    )


    canvas.line(
        14 * mm,
        20 * mm,
        page_width - 14 * mm,
        20 * mm
    )


    # --------------------------------------------------------
    # DATEN
    # --------------------------------------------------------

    calories = (
        f"{plan.calories} kcal"
        if plan.calories
        else "Nicht berechnet"
    )


    allergies = split_lines(
        plan.allergies_snapshot
    )


    excluded_foods = split_lines(
        plan.excluded_foods_snapshot
    )


    allergies_text = (
        ", ".join(allergies)
        if allergies
        else "Keine"
    )


    excluded_text = (
        ", ".join(
            excluded_foods
        )
        if excluded_foods
        else "Keine"
    )


    # --------------------------------------------------------
    # FUSSZEILEN-TABELLE
    # --------------------------------------------------------

    footer_data = [
        [
            [
                Paragraph(
                    "Kalorienziel",
                    styles["footer_label"]
                ),

                Paragraph(
                    escape(calories),
                    styles["footer_text"]
                ),
            ],

            [
                Paragraph(
                    "Allergien",
                    styles["footer_label"]
                ),

                Paragraph(
                    escape(
                        allergies_text
                    ),
                    styles["footer_text"]
                ),
            ],

            [
                Paragraph(
                    "Unerwünschte Lebensmittel",
                    styles["footer_label"]
                ),

                Paragraph(
                    escape(
                        excluded_text
                    ),
                    styles["footer_text"]
                ),
            ],
        ]
    ]


    footer_table = Table(
        footer_data,
        colWidths=[
            52 * mm,
            92 * mm,
            124 * mm,
        ]
    )


    footer_table.setStyle(
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
                2
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                4
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                0
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                0
            ),
        ])
    )


    footer_table.wrap(
        page_width - 28 * mm,
        16 * mm
    )


    footer_table.drawOn(
        canvas,
        14 * mm,
        8 * mm
    )


    canvas.restoreState()


# ============================================================
# ERNÄHRUNGSPLAN PDF
# ============================================================

def generate_nutrition_pdf(
    plan,
    user,
    profile,
    file_path
):
    """
    Erstellt den Ernährungsplan.

    Eigenschaften:
    - weißer Hintergrund
    - Love Yourself Logo
    - Überschrift "Ernährungsplan"
    - zwei Tage pro Seite
    - sichtbare Rezepte
    - echte abgerundete Tabellen
    - kompakte Fußzeile
    """

    nutrition_days = parse_json_data(
        plan.nutrition_data,
        []
    )


    styles = (
        create_nutrition_styles()
    )


    # ========================================================
    # DOKUMENT
    # ========================================================

    document = SimpleDocTemplate(
        file_path,

        pagesize=landscape(
            A4
        ),

        leftMargin=14 * mm,
        rightMargin=14 * mm,

        topMargin=9 * mm,

        bottomMargin=25 * mm,

        title="Ernährungsplan",

        author="Love Yourself",
    )


    story = []


    # ========================================================
    # LEERER PLAN
    # ========================================================

    if not nutrition_days:

        story.append(
            build_page_header(
                styles
            )
        )


        story.append(
            Spacer(
                1,
                4 * mm
            )
        )


        story.append(
            Paragraph(
                (
                    "Für diesen Plan sind "
                    "keine Ernährungstage gespeichert."
                ),
                styles["body_center"]
            )
        )


    # ========================================================
    # TAGE
    # ========================================================

    else:

        for index, nutrition_day in enumerate(
            nutrition_days
        ):


            # ------------------------------------------------
            # KOPF AM ANFANG JEDER SEITE
            # ------------------------------------------------

            if index % 2 == 0:

                story.append(
                    build_page_header(
                        styles
                    )
                )


                story.append(
                    Spacer(
                        1,
                        3 * mm
                    )
                )


            # ------------------------------------------------
            # TAG
            # ------------------------------------------------

            story.append(
                build_nutrition_day(
                    nutrition_day,
                    styles
                )
            )


            # ------------------------------------------------
            # ABSTAND ZWISCHEN DEN BEIDEN TAGEN
            # ------------------------------------------------

            if (
                index % 2 == 0
                and index
                < len(
                    nutrition_days
                ) - 1
            ):

                story.append(
                    Spacer(
                        1,
                        4 * mm
                    )
                )


            # ------------------------------------------------
            # NACH JEDEM ZWEITEN TAG NEUE SEITE
            # ------------------------------------------------

            if (
                index % 2 == 1
                and index
                < len(
                    nutrition_days
                ) - 1
            ):

                story.append(
                    PageBreak()
                )


    # ========================================================
    # PDF BAUEN
    # ========================================================

    def page_footer(
        canvas,
        doc
    ):

        draw_nutrition_footer(
            canvas,
            doc,
            plan,
            styles
        )


    document.build(
        story,

        onFirstPage=page_footer,

        onLaterPages=page_footer,
    )