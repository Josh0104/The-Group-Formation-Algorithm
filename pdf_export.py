from __future__ import annotations

import os
from collections import defaultdict
from datetime import datetime
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from iso3166 import countries


from person import Person, Gender, AgeGroup


def export_teams_pdf(
    campers: list[Person],
    output_dir: str = "output",
    filename: str | None = None,
) -> str:
    """
    Export team results to a landscape PDF.

    Parameters
    ----------
    campers:
        List of Person objects after teams have been assigned.
    output_dir:
        Directory where the PDF should be saved.
    filename:
        Optional custom file name. If omitted, a timestamped file name is used.

    Returns
    -------
    str
        Path to the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = f"teams_{timestamp}.pdf"

    output_path = os.path.join(output_dir, filename)

    grouped_teams = group_campers_by_team(campers)
    team_stats = {team: compute_team_stats(members) for team, members in grouped_teams.items()}

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        # pagesize=landscape(A4),
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    styles = build_styles()
    story = []

    story.append(Paragraph("Camp Team Formation Results", styles["title"]))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        styles["meta"],
    ))
    story.append(Spacer(1, 6 * mm))

    story.append(build_summary_table(grouped_teams, team_stats, styles))
    story.append(Spacer(1, 8 * mm))

    for team_number, members in grouped_teams.items():
        story.append(build_team_section(team_number, members, team_stats[team_number], styles))
        story.append(Spacer(1, 6 * mm))

    doc.build(story)
    return output_path


def group_campers_by_team(campers: Iterable[Person]) -> dict[int, list[Person]]:
    """Group campers by assigned team number."""
    grouped: dict[int, list[Person]] = defaultdict(list)

    for camper in campers:
        if camper.team is None:
            continue
        grouped[camper.team].append(camper)

    # Sort team members alphabetically for cleaner output
    for team in grouped:
        grouped[team] = sorted(
            grouped[team],
            key=lambda p: (p.first_name.lower(), p.last_name.lower()),
        )

    return dict(sorted(grouped.items(), key=lambda item: item[0]))


def compute_team_stats(team_members: list[Person]) -> dict[str, int]:
    """Compute summary statistics for one team."""
    return {
        "total": len(team_members),
        "leadership": sum(p.a1.value for p in team_members),
        "creativity": sum(p.a2.value for p in team_members),
        "bible_knowledge": sum(p.a3.value for p in team_members),
        "physical_fit": sum(p.a4.value for p in team_members),
        "musicians": sum(p.a5.value for p in team_members),
        "camp_experience": sum(p.a6.value for p in team_members),
        "acting": sum(p.a7.value for p in team_members),
        "prop_design": sum(p.a8.value for p in team_members),
        "men": sum(1 for p in team_members if p.age_group == AgeGroup.MEN),
        "women": sum(1 for p in team_members if p.age_group == AgeGroup.WOMEN),
        "youth": sum(1 for p in team_members if p.age_group == AgeGroup.YOUTH),
        "kids": sum(1 for p in team_members if p.age_group == AgeGroup.KIDS),
        "babies": sum(1 for p in team_members if p.age_group == AgeGroup.BABIES),
    }


def build_styles() -> dict[str, ParagraphStyle]:
    """Create custom styles for the PDF."""
    sample = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "CustomTitle",
            parent=sample["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=6,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=sample["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#6B7280"),
        ),
        "section_title": ParagraphStyle(
            "SectionTitle",
            parent=sample["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.white,
            backColor=colors.HexColor("#2563EB"),
            leftIndent=4,
            spaceAfter=6,
            spaceBefore=4,
        ),
        "normal": ParagraphStyle(
            "CustomNormal",
            parent=sample["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#111827"),
        ),
        "small": ParagraphStyle(
            "Small",
            parent=sample["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#374151"),
        ),
    }


def build_summary_table(
    grouped_teams: dict[int, list[Person]],
    team_stats: dict[int, dict[str, int]],
    styles: dict[str, ParagraphStyle],
) -> Table:
    """Build the first overview table showing totals per team."""
    header = [
        "Team",
        "Total",
        "Men",
        "Women",
        "Youth",
        "Kids",
        "Babies",
        "Leadership",
        "Creativity",
        "Bible",
        "Physical",
        "Music",
        "Experience",
        "Acting",
        "Props",
    ]

    rows = [header]

    for team_number, _members in grouped_teams.items():
        stats = team_stats[team_number]
        rows.append([
            f"Team {team_number}",
            stats["total"],
            stats["men"],
            stats["women"],
            stats["youth"],
            stats["kids"],
            stats["babies"],
            stats["leadership"],
            stats["creativity"],
            stats["bible_knowledge"],
            stats["physical_fit"],
            stats["musicians"],
            stats["camp_experience"],
            stats["acting"],
            stats["prop_design"],
        ])

    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D4ED8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.whitesmoke,
            colors.HexColor("#F9FAFB"),
        ]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def build_team_section(
    team_number: int,
    members: list[Person],
    stats: dict[str, int],
    styles: dict[str, ParagraphStyle],
) -> KeepTogether:
    """Build one full section for a team."""
    content = []

    content.append(Paragraph(
        f"Team {team_number} &nbsp;&nbsp;|&nbsp;&nbsp; Total: {stats['total']}",
        styles["section_title"],
    ))

    content.append(build_team_stats_table(stats))
    content.append(Spacer(1, 3 * mm))
    content.append(build_members_table(members))

    return KeepTogether(content)


def build_team_stats_table(stats: dict[str, int]) -> Table:
    """Small stat block shown before the member list."""
    total_score = stats["leadership"] + stats["creativity"] + stats["bible_knowledge"] + stats["physical_fit"] + stats["musicians"] + stats["camp_experience"] + stats["acting"] + stats["prop_design"]
    data = [
        ["Men", stats["men"], "Women", stats["women"], "Youth", stats["youth"], "Kids", stats["kids"], "Babies", stats["babies"]],
        ["Leadership", stats["leadership"], "Creativity", stats["creativity"], "Bible", stats["bible_knowledge"], "Physical", stats["physical_fit"], "Music", stats["musicians"]],
        ["Experience", stats["camp_experience"], "Acting", stats["acting"], "Props", stats["prop_design"], "Total Score", total_score, "", "", "", ""],
    ]

    table = Table(data, colWidths=[22 * mm, 10 * mm] * 5)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BFDBFE")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTNAME", (4, 0), (4, -1), "Helvetica-Bold"),
        ("FONTNAME", (6, 0), (6, -1), "Helvetica-Bold"),
        ("FONTNAME", (8, 0), (8, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def build_members_table(members: list[Person]) -> Table:
    """Detailed member table for one team."""
    rows = [[
        "#",
        "First name",
        "Last name",
        # "Age",
        "Gender",
        "Country",
        "Group",
        # "Roles",
    ]]

    for index, person in enumerate(members, start=1):
        if person.country:
            country_name = countries.get(person.country).name
            if len(country_name) > 15: # if country name is too long
                country_name = person.country
        else:
            country_name = "-"
        
        rows.append([
            index,
            person.first_name,
            person.last_name,
            # person.get_age(),
            person.gender.name.title(),
            country_name,
            person.age_group.name.title(),
            # build_role_string(person),
        ])

    table = Table(
        rows,
        repeatRows=1,
        colWidths=[10 * mm, 32 * mm, 32 * mm, 12 * mm, 18 * mm, 24 * mm, 22 * mm, 70 * mm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DBEAFE")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D1D5DB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F9FAFB"),
        ]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def build_role_string(person: Person) -> str:
    """Return a readable text version of a person's skills/roles."""
    roles = []

    if person.a1 and person.a1.value > 0:
        roles.append(f"Leadership: {person.a1.name.title()}")
    if person.a2 and person.a2.value > 0:
        roles.append(f"Creativity: {person.a2.name.title()}")
    if person.a3 and person.a3.value > 0:
        roles.append(f"Bible: {person.a3.name.title()}")
    if person.a4 and person.a4.value > 0:
        roles.append(f"Physical: {person.a4.name.title()}")
    if person.a5 and person.a5.value > 0:
        roles.append(f"Music: {person.a5.name.title()}")
    if person.a6 and person.a6.value > 0:
        roles.append(f"Experience: {person.a6.name.title()}")
    if person.a7 and person.a7.value > 0:
        roles.append(f"Acting: {person.a7.name.title()}")
    if person.a8 and person.a8.value > 0:
        roles.append(f"Props: {person.a8.name.title()}")

    return ", ".join(roles) if roles else "-"