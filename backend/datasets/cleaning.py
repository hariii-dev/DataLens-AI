import pandas as pd
from django.core.files.base import ContentFile
from io import BytesIO


def clean_dataset(dataset, remove_duplicates=True, fill_missing=False):
    dataset.file.open('rb')

    try:
        if dataset.file_type == 'csv':
            df = pd.read_csv(dataset.file)
        else:
            df = pd.read_excel(dataset.file, engine='openpyxl')
    finally:
        dataset.file.close()

    original_rows = len(df)

    if remove_duplicates:
        df = df.drop_duplicates()

    if fill_missing:
        for column in df.columns:
            if df[column].isnull().any():
                if pd.api.types.is_numeric_dtype(df[column]):
                    median = df[column].median()
                    df[column] = df[column].fillna(
                        median if pd.notna(median) else 0
                    )
                else:
                    df[column] = df[column].fillna('Unknown')

    buffer = BytesIO()

    if dataset.file_type == 'csv':
        df.to_csv(buffer, index=False)
        filename = f'{dataset.name}_cleaned.csv'
    else:
        df.to_excel(buffer, index=False, engine='openpyxl')
        filename = f'{dataset.name}_cleaned.xlsx'

    buffer.seek(0)

    dataset.cleaned_file.save(
        filename,
        ContentFile(buffer.read()),
        save=True
    )

    return {
        'original_rows': original_rows,
        'cleaned_rows': len(df),
        'removed_duplicates': original_rows - len(df),
        'remaining_missing_values': int(df.isnull().sum().sum()),
        'cleaned_file': dataset.cleaned_file.url,
    }
