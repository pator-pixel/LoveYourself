from pathlib import Path

from pdf import (
    generate_fitness_pdf,
    generate_nutrition_pdf,
    generate_shopping_pdf,
)


PDF_GENERATORS = {
    "nutrition": (
        generate_nutrition_pdf,
        "nutrition_plan",
        "nutrition_title",
    ),
    "fitness": (
        generate_fitness_pdf,
        "fitness_plan",
        "fitness_title",
    ),
    "shopping": (
        generate_shopping_pdf,
        "shopping_list",
        "shopping_title",
    ),
}


def create_plan_pdf(
    *,
    pdf_type,
    plan,
    user,
    profile,
    excluded_items=None,
):
    """
    Erzeugt eine PDF-Datei und liefert
    Dateipfad und Downloadnamen.
    """

    if pdf_type not in PDF_GENERATORS:
        raise ValueError(
            f"Unbekannter PDF-Typ: {pdf_type}"
        )

    generator, file_prefix, title_attribute = (
        PDF_GENERATORS[pdf_type]
    )

    output_folder = Path(
        "generated_pdfs"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = output_folder / (
        f"{file_prefix}_{plan.id}.pdf"
    )


    if pdf_type == "shopping":

        generator(
            plan=plan,
            user=user,
            profile=profile,
            file_path=str(file_path),
            excluded_items=(
                excluded_items
                or []
            )
        )

    else:

        generator(
            plan=plan,
            user=user,
            profile=profile,
            file_path=str(file_path)
        )


    download_name = (
        f"{getattr(plan, title_attribute)}.pdf"
    )

    return (
        str(file_path),
        download_name
    )