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


def generate_ai_response(prompt):
    from django.conf import settings
    from google import genai
    from google.genai import types

    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key is missing.")

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=1024
        )
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()
