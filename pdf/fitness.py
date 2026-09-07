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
)


# ============================================================
# FARBEN
# ============================================================

VERY_LIGHT_SAGE = colors.HexColor(
    "#F3F6F1"
)

LIGHT_SAGE_LINE = colors.HexColor(
    "#D6DDD3"
)

ROUNDED_BORDER = colors.HexColor(
    "#AEBBA9"
)

FOOTER_LINE = colors.HexColor(
    "#DADFD8"
)

SOFT_BEIGE = colors.HexColor(
    "#F7F3EA"
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
# ABGERUNDETER RAHMEN
# ============================================================

class RoundedTableBox(Flowable):
    """
    Zeichnet eine Tabelle mit sauber abgerundeten
    Außenkanten.

    Die Tabelle wird zuerst auf die runde Form beschnitten.
    Danach wird der Außenrahmen erneut darüber gezeichnet.
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


        # ----------------------------------------------------
        # TABELLE AUF RUNDUNG BESCHNEIDEN
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # AUSSENRAHMEN DARÜBER ZEICHNEN
        # ----------------------------------------------------

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

def create_fitness_styles():
    """
    Ergänzt die allgemeinen PDF-Styles
    um Fitnessplan-Styles.
    """

    styles = create_styles()


    styles["fitness_title"] = ParagraphStyle(
        "FitnessTitle",
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=20,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
        spaceAfter=0,
    )


    styles["day_title"] = ParagraphStyle(
        "FitnessDayTitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
        spaceAfter=2 * mm,
    )


    styles["exercise_name"] = ParagraphStyle(
        "FitnessExerciseName",
        fontName="Helvetica-Bold",
        fontSize=8.2,
        leading=10,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
        spaceAfter=2,
    )


    styles["exercise_meta_label"] = ParagraphStyle(
        "FitnessMetaLabel",
        fontName="Helvetica-Bold",
        fontSize=5.7,
        leading=6.6,
        textColor=TEXT_SOFT,
        alignment=TA_LEFT,
    )


    styles["exercise_meta_value"] = ParagraphStyle(
        "FitnessMetaValue",
        fontName="Helvetica-Bold",
        fontSize=6.4,
        leading=7.4,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
    )


    styles["instructions_heading"] = ParagraphStyle(
        "FitnessInstructionsHeading",
        fontName="Helvetica-Bold",
        fontSize=6.2,
        leading=7.2,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
        spaceBefore=2,
        spaceAfter=2,
    )


    styles["instructions_text"] = ParagraphStyle(
        "FitnessInstructionsText",
        fontName="Helvetica",
        fontSize=5.9,
        leading=7.1,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
    )


    styles["steps_label"] = ParagraphStyle(
        "FitnessStepsLabel",
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=7.5,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
    )


    styles["steps_text"] = ParagraphStyle(
        "FitnessStepsText",
        fontName="Helvetica",
        fontSize=6.5,
        leading=7.5,
        textColor=TEXT_DARK,
        alignment=TA_LEFT,
    )


    styles["footer_label"] = ParagraphStyle(
        "FitnessFooterLabel",
        fontName="Helvetica-Bold",
        fontSize=5.7,
        leading=6.5,
        textColor=DARK_GREEN,
        alignment=TA_LEFT,
    )


    styles["footer_text"] = ParagraphStyle(
        "FitnessFooterText",
        fontName="Helvetica",
        fontSize=5.5,
        leading=6.4,
        textColor=TEXT_SOFT,
        alignment=TA_LEFT,
    )


    return styles


# ============================================================
# KOPFZEILE
# ============================================================

def build_page_header(styles):
    """
    Erstellt Logo + Überschrift Fitnessplan.
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
        "Fitnessplan",
        styles["fitness_title"]
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
# ÜBUNGSZELLE
# ============================================================

def create_exercise_cell(
    exercise,
    styles
):
    """
    Erstellt eine kompakte Übungskarte für die PDF.

    Enthalten:
    - Name
    - Sätze
    - Wiederholungen / Dauer
    - Pause
    - vollständige Ausführung
    """

    exercise = exercise or {}


    name = safe_text(
        exercise.get("name"),
        "Nicht angegeben"
    )


    sets = safe_text(
        exercise.get("sets"),
        "-"
    )


    repetitions = safe_text(
        exercise.get("repetitions"),
        "-"
    )


    pause = safe_text(
        exercise.get("pause"),
        "-"
    )


    instructions = safe_text(
        exercise.get("instructions"),
        ""
    )


    # --------------------------------------------------------
    # FALLBACK FÜR ALTE FITNESSPLÄNE
    # --------------------------------------------------------

    if not instructions:

        instructions = (
            "Für diesen älteren Plan wurde noch keine "
            "ausführliche Übungsbeschreibung gespeichert."
        )


    content = []


    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    content.append(
        Paragraph(
            escape(name),
            styles["exercise_name"]
        )
    )


    # --------------------------------------------------------
    # META-DATEN
    # --------------------------------------------------------

    meta_table = Table(
        [
            [
                [
                    Paragraph(
                        "Sätze",
                        styles["exercise_meta_label"]
                    ),
                    Paragraph(
                        escape(sets),
                        styles["exercise_meta_value"]
                    ),
                ],

                [
                    Paragraph(
                        "Wiederholungen / Dauer",
                        styles["exercise_meta_label"]
                    ),
                    Paragraph(
                        escape(repetitions),
                        styles["exercise_meta_value"]
                    ),
                ],

                [
                    Paragraph(
                        "Pause",
                        styles["exercise_meta_label"]
                    ),
                    Paragraph(
                        escape(pause),
                        styles["exercise_meta_value"]
                    ),
                ],
            ]
        ],
        colWidths=[
            26 * mm,
            48 * mm,
            29 * mm,
        ]
    )


    meta_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                VERY_LIGHT_SAGE
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
                4
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
                4
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                4
            ),
        ])
    )


    content.append(
        meta_table
    )


    content.append(
        Spacer(
            1,
            1.2 * mm
        )
    )


    # --------------------------------------------------------
    # AUSFÜHRUNG
    # --------------------------------------------------------

    content.append(
        Paragraph(
            "Ausführung",
            styles["instructions_heading"]
        )
    )


    content.append(
        Paragraph(
            escape(instructions),
            styles["instructions_text"]
        )
    )


    return KeepInFrame(
        maxWidth=116 * mm,
        maxHeight=53 * mm,
        content=content,
        mode="shrink",
        hAlign="LEFT",
        vAlign="TOP",
    )


# ============================================================
# TRAININGSTAG
# ============================================================

def build_fitness_day(
    fitness_day,
    styles
):
    """
    Baut einen kompletten Trainingstag.

    Die Übungen erscheinen in zwei Spalten.
    Dadurch bleiben die Beschreibungen gut lesbar,
    ohne dass die PDF unnötig viele Seiten bekommt.
    """

    day_number = safe_text(
        fitness_day.get("day"),
        ""
    )


    day_title = Paragraph(
        f"Tag {escape(day_number)}",
        styles["day_title"]
    )


    exercises = fitness_day.get(
        "exercises",
        []
    )


    # --------------------------------------------------------
    # ÜBUNGEN IN 2 SPALTEN VERTEILEN
    # --------------------------------------------------------

    exercise_rows = []


    for index in range(
        0,
        len(exercises),
        2
    ):

        left_exercise = exercises[index]


        if index + 1 < len(exercises):

            right_exercise = exercises[
                index + 1
            ]

        else:

            right_exercise = None


        left_cell = create_exercise_cell(
            left_exercise,
            styles
        )


        right_cell = (
            create_exercise_cell(
                right_exercise,
                styles
            )
            if right_exercise
            else ""
        )


        exercise_rows.append([
            left_cell,
            right_cell
        ])


    # --------------------------------------------------------
    # KEINE ÜBUNGEN
    # --------------------------------------------------------

    if not exercise_rows:

        exercise_rows = [
            [
                Paragraph(
                    "Keine Übungen gespeichert.",
                    styles["instructions_text"]
                ),
                ""
            ]
        ]


    exercise_table = Table(
        exercise_rows,
        colWidths=[
            126 * mm,
            126 * mm,
        ],
        hAlign="CENTER",
    )


    exercise_table.setStyle(
        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                WHITE
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.35,
                LIGHT_SAGE_LINE
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
                6
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
        ])
    )


    rounded_exercises = RoundedTableBox(
        exercise_table,
        radius=2.8 * mm,
        border_color=ROUNDED_BORDER,
        border_width=0.8,
    )


    # --------------------------------------------------------
    # SCHRITTE-ALTERNATIVE
    # --------------------------------------------------------

    steps_text = safe_text(
        fitness_day.get(
            "steps_alternative"
        ),
        "Keine Angabe"
    )


    steps_table = Table(
        [
            [
                Paragraph(
                    "Keine Zeit für das Training?",
                    styles["steps_label"]
                ),

                Paragraph(
                    escape(steps_text),
                    styles["steps_text"]
                )
            ]
        ],
        colWidths=[
            61 * mm,
            191 * mm
        ],
        hAlign="CENTER"
    )


    steps_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                SOFT_BEIGE
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.45,
                LIGHT_SAGE_LINE
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
                5
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
        ])
    )


    return KeepTogether([
        day_title,
        rounded_exercises,
        Spacer(
            1,
            2.5 * mm
        ),
        steps_table,
    ])


# ============================================================
# FUSSZEILE
# ============================================================

def draw_fitness_footer(
    canvas,
    document,
    plan,
    profile,
    styles
):
    """
    Kompakte Fitness-Fußzeile.

    Enthalten:
    - Fitnesslevel
    - Trainingstage
    - aktuelles Gewicht
    """

    canvas.saveState()


    page_width, _ = landscape(
        A4
    )


    # --------------------------------------------------------
    # LINIE
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

    fitness_level = safe_text(
        getattr(
            profile,
            "fitness_level",
            None
        ),
        "Nicht angegeben"
    )


    training_days = safe_text(
        getattr(
            profile,
            "training_days",
            None
        ),
        "Nicht angegeben"
    )


    current_weight = (
        f"{plan.current_weight} kg"
        if plan.current_weight is not None
        else "Nicht angegeben"
    )


    footer_data = [
        [
            [
                Paragraph(
                    "Fitnesslevel",
                    styles["footer_label"]
                ),

                Paragraph(
                    escape(fitness_level),
                    styles["footer_text"]
                ),
            ],

            [
                Paragraph(
                    "Trainingstage",
                    styles["footer_label"]
                ),

                Paragraph(
                    escape(training_days),
                    styles["footer_text"]
                ),
            ],

            [
                Paragraph(
                    "Aktuelles Gewicht",
                    styles["footer_label"]
                ),

                Paragraph(
                    escape(current_weight),
                    styles["footer_text"]
                ),
            ],
        ]
    ]


    footer_table = Table(
        footer_data,
        colWidths=[
            90 * mm,
            90 * mm,
            88 * mm,
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
# FITNESSPLAN PDF
# ============================================================

def generate_fitness_pdf(
    plan,
    user,
    profile,
    file_path
):
    """
    Erstellt den Fitnessplan.

    Eigenschaften:
    - weißer Hintergrund
    - Love Yourself Logo
    - Überschrift nur "Fitnessplan"
    - vollständige Übungsausführungen direkt sichtbar
    - keine separate Übungsalternative
    - Schritte-Alternative pro Trainingstag
    - abgerundete Trainingsbereiche
    - möglichst kompakte Seitennutzung
    """

    fitness_days = parse_json_data(
        plan.fitness_data,
        []
    )


    styles = (
        create_fitness_styles()
    )


    document = SimpleDocTemplate(
        file_path,

        pagesize=landscape(
            A4
        ),

        leftMargin=14 * mm,
        rightMargin=14 * mm,

        topMargin=9 * mm,

        bottomMargin=25 * mm,

        title="Fitnessplan",

        author="Love Yourself",
    )


    story = []


    # ========================================================
    # KEINE TRAININGSTAGE
    # ========================================================

    if not fitness_days:

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
                    "keine Trainingstage gespeichert."
                ),
                styles["body_center"]
            )
        )


    # ========================================================
    # TRAININGSTAGE
    # ========================================================

    else:

        for index, fitness_day in enumerate(
            fitness_days
        ):


            # ------------------------------------------------
            # KOPFZEILE
            #
            # Zwei Trainingstage pro Seite werden versucht.
            # Durch KeepTogether wird ein kompletter Tag
            # auf die nächste Seite geschoben, wenn der
            # verbleibende Platz nicht reicht.
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
            # TRAININGSTAG
            # ------------------------------------------------

            story.append(
                build_fitness_day(
                    fitness_day,
                    styles
                )
            )


            # ------------------------------------------------
            # ABSTAND
            # ------------------------------------------------

            if (
                index % 2 == 0
                and index
                < len(
                    fitness_days
                ) - 1
            ):

                story.append(
                    Spacer(
                        1,
                        4 * mm
                    )
                )


            # ------------------------------------------------
            # MAXIMAL ZWEI TRAININGSTAGE PRO SEITE
            # ------------------------------------------------

            if (
                index % 2 == 1
                and index
                < len(
                    fitness_days
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

        draw_fitness_footer(
            canvas,
            doc,
            plan,
            profile,
            styles
        )


    document.build(
        story,

        onFirstPage=page_footer,

        onLaterPages=page_footer,
    )