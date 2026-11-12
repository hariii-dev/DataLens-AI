import pandas as pd


def build_dataset_context(dataset):
    dataset.file.open('rb')

    try:
        if dataset.file_type == 'csv':
            df = pd.read_csv(dataset.file)
        else:
            df = pd.read_excel(
                dataset.file,
                engine='openpyxl'
            )

        return {
            'dataset_name': dataset.name,
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'columns': [
                {
                    'name': str(column),
                    'data_type': str(df[column].dtype),
                    'missing_values': int(df[column].isna().sum()),
                    'unique_values': int(df[column].nunique()),
                }
                for column in df.columns
            ],
            'sample_data': df.head(20).astype(object).where(
                pd.notna(df.head(20)), None
            ).to_dict(orient='records'),
            'numeric_summary': df.describe(
                include='number'
            ).to_dict(),
        }

    finally:
        dataset.file.close()


def build_ai_prompt(question, context):
    return f"""
You are DataLens AI, a data analytics assistant.

Analyze only the dataset information provided below.
Never invent values or unsupported conclusions.
Distinguish correlation from causation.
If the available data cannot answer a question, say so.

DATASET:
{context}

USER QUESTION:
{question}

Provide a clear, concise answer with relevant data evidence.
"""
