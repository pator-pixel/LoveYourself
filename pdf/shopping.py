from html import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from pdf.common import (
    DARK_GREEN,
    LIGHT_SAGE,
    SAGE_GREEN,
    WHITE,
    create_styles,
    draw_shopping_page,
    format_date,
    html_text,
    parse_json_data,
    safe_text,
)


# =========================================================
# EINZELNE EINKAUFS-KATEGORIE
# =========================================================

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
                        escape(
                            safe_text(item)
                        ),
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

        content.append(
            item_table
        )

        content.append(
            Spacer(
                1,
                1.5 * mm
            )
        )


    category_box = Table(
        [[content]],
        colWidths=[
            82 * mm
        ]
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


# =========================================================
# EINKAUFSLISTEN-PDF
# =========================================================

def generate_shopping_pdf(
    plan,
    user,
    profile,
    file_path,
    excluded_items=None
):
    """
    Erstellt die Einkaufsliste als PDF.

    excluded_items enthält Lebensmittel,
    die der Benutzer auf der Website
    durchgestrichen hat.
    """

    shopping_categories = parse_json_data(
        plan.shopping_data,
        []
    )


    # =====================================================
    # DURCHGESTRICHENE LEBENSMITTEL ENTFERNEN
    # =====================================================

    excluded_items = {
        str(item).strip()
        for item in (
            excluded_items
            or []
        )
        if str(item).strip()
    }


    if excluded_items:

        filtered_categories = []


        for category in shopping_categories:

            category_items = category.get(
                "items",
                []
            )


            filtered_items = [
                item
                for item in category_items
                if str(item).strip()
                not in excluded_items
            ]


            if filtered_items:

                filtered_categories.append({
                    "category": category.get(
                        "category",
                        "Sonstiges"
                    ),
                    "items": filtered_items
                })


        shopping_categories = (
            filtered_categories
        )


    # =====================================================
    # PDF-DOKUMENT
    # =====================================================

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


    # =====================================================
    # TITEL
    # =====================================================

    story.append(
        Paragraph(
            html_text(
                plan.shopping_title
            ),
            styles["title"]
        )
    )


    story.append(
        Paragraph(
            (
                f"Für "
                f"{html_text(user.username)}"
                f" | "
                f"{format_date(plan.created_at)}"
            ),
            styles["subtitle"]
        )
    )


    story.append(
        Spacer(
            1,
            3 * mm
        )
    )


    # =====================================================
    # HINWEISBOX
    # =====================================================

    if excluded_items:

        note_text = (
            "<b>Deine aktualisierte Einkaufsliste</b><br/>"
            "Lebensmittel, die du bereits zu Hause hast, "
            "wurden aus dieser Liste entfernt."
        )

    else:

        note_text = (
            "<b>Deine Einkaufsliste</b><br/>"
            "Streiche vorhandene Zutaten von deiner Liste."
        )


    note_table = Table(
        [
            [
                Paragraph(
                    note_text,
                    styles["body_center"]
                )
            ]
        ],
        colWidths=[
            160 * mm
        ]
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


    story.append(
        note_table
    )

    story.append(
        Spacer(
            1,
            7 * mm
        )
    )


    # =====================================================
    # KATEGORIEN
    # =====================================================

    category_boxes = [
        build_shopping_category_box(
            category,
            styles
        )
        for category
        in shopping_categories
    ]


    rows = []


    for index in range(
        0,
        len(category_boxes),
        2
    ):

        first_box = (
            category_boxes[index]
        )


        second_box = (
            category_boxes[index + 1]
            if index + 1
            < len(category_boxes)
            else ""
        )


        rows.append([
            first_box,
            second_box
        ])


    # =====================================================
    # LISTE LEER
    # =====================================================

    if not rows:

        if excluded_items:

            empty_text = (
                "Du hast bereits alle Lebensmittel "
                "auf deiner Einkaufsliste zu Hause."
            )

        else:

            empty_text = (
                "Keine Einkaufsliste vorhanden."
            )


        rows = [
            [
                Paragraph(
                    empty_text,
                    styles["body_center"]
                ),
                ""
            ]
        ]


    # =====================================================
    # EINKAUFS-GRID
    # =====================================================

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


    story.append(
        shopping_grid
    )


    # =====================================================
    # PDF ERSTELLEN
    # =====================================================

    document.build(
        story,
        onFirstPage=draw_shopping_page,
        onLaterPages=draw_shopping_page
    )