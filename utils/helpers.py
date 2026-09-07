import json
import random
import string

from flask import request


def generate_temporary_password():
    """Erstellt ein zufälliges temporäres Passwort."""

    random_part = "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=8
        )
    )

    return f"Love{random_part}!"


def clean_profile_value(value):
    """Verhindert leere Werte in AI-Prompts."""

    if value is None or value == "":
        return "Keine Angabe"

    return value


def parse_json_data(json_text, fallback):
    """
    Wandelt gespeicherte JSON-Texte wieder in
    Python-Listen oder Dictionaries um.
    """

    if not json_text:
        return fallback

    try:
        return json.loads(json_text)

    except (
        json.JSONDecodeError,
        TypeError
    ):
        return fallback


def form_list(field_name):
    """
    Liest mehrere dynamische Formularfelder ein
    und speichert sie zeilenweise.
    """

    return "\n".join(
        item.strip()
        for item in request.form.getlist(field_name)
        if item.strip()
    )


def join_selected_values(values):
    """
    Wandelt ausgewählte Checkbox-Werte in
    einen zeilenweisen Text um.
    """

    return "\n".join(
        value.strip()
        for value in values
        if value.strip()
    )


def merge_lines(existing_value, new_value):
    """
    Fügt neue Angaben zu einem bestehenden
    zeilenweisen Text hinzu.

    Doppelte Einträge werden vermieden.
    """

    existing_items = []

    if existing_value:
        existing_items = [
            item.strip()
            for item in existing_value.splitlines()
            if item.strip()
        ]

    new_items = []

    if new_value:
        new_items = [
            item.strip()
            for item in new_value.splitlines()
            if item.strip()
        ]

    combined_items = existing_items.copy()

    known_items = {
        item.casefold()
        for item in combined_items
    }

    for item in new_items:
        normalized_item = item.casefold()

        if normalized_item not in known_items:
            combined_items.append(item)
            known_items.add(normalized_item)

    return "\n".join(combined_items)


def combine_choice_fields(
    checkbox_field,
    custom_field
):
    """
    Verbindet vorgegebene Auswahlchips mit
    einem freien Sonstiges-Feld.
    """

    selected_values = [
        value.strip()
        for value in request.form.getlist(
            checkbox_field
        )
        if value.strip()
    ]

    custom_value = request.form.get(
        custom_field,
        ""
    ).strip()

    if custom_value:
        custom_items = [
            item.strip()
            for item in custom_value.splitlines()
            if item.strip()
        ]

        known_items = {
            value.casefold()
            for value in selected_values
        }

        for item in custom_items:
            normalized_item = item.casefold()

            if normalized_item not in known_items:
                selected_values.append(item)
                known_items.add(normalized_item)

    return "\n".join(selected_values)
