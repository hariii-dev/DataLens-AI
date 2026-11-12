from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from analytics.services import generate_analytics


def generate_pdf_report(dataset):
    analytics = generate_analytics(dataset)
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("DataLens AI - Analytics Report", styles['Title'])
    )
    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph(f"Dataset: {dataset.name}", styles['Heading2'])
    )
    elements.append(
        Paragraph(f"Total Rows: {analytics['total_rows']}", styles['Normal'])
    )
    elements.append(
        Paragraph(f"Total Columns: {analytics['total_columns']}", styles['Normal'])
    )
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph("Numeric Statistics", styles['Heading2'])
    )

    table_data = [
        ['Column', 'Mean', 'Median', 'Minimum', 'Maximum']
    ]

    for column, stats in analytics['numeric_statistics'].items():
        table_data.append([
            column,
            str(stats['mean']),
            str(stats['median']),
            str(stats['minimum']),
            str(stats['maximum']),
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph("Categorical Statistics", styles['Heading2'])
    )

    for column, stats in analytics['categorical_statistics'].items():
        elements.append(
            Paragraph(
                f"{column}: {stats['unique_values']} unique values; "
                f"Most common: {stats['most_common']} "
                f"({stats['most_common_count']} occurrences)",
                styles['Normal']
            )
        )
        elements.append(Spacer(1, 6))

    document.build(elements)
    buffer.seek(0)

    return buffer
