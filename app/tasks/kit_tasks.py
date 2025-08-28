from app.core.celery_app import celery_app
import openai
import json

from app.core.config import settings

# Set Gemini API Key
def _init_openai():
    openai.api_key = settings.GEMINI_API_KEY

_init_openai()

@celery_app.task(name="generate_application_kit")
def generate_application_kit(resume_data: dict, job_description: str) -> dict:
    # Prompt from frontend: structuredContentPrompt
    prompt = f"""
You are an expert career coach and professional writer. Your task is to generate a suite of job application materials.
Analyze the provided RESUME and JOB DESCRIPTION.
Generate three assets: 1) a short application email, 2) a professional cover letter, and 3) a set of 7-10 interview questions with answers.

Formatting rules:
- For the email and cover letter, use '\n\n' for paragraph breaks.
- To emphasize key skills or experiences that directly match the job description, wrap them in double asterisks, like **this**.
- Adhere strictly to the JSON schema. Do not include any introductory text or markdown formatting in your response.

--- RESUME ---
{json.dumps(resume_data)}

--- JOB DESCRIPTION ---
{job_description}
"""
    response = openai.ChatCompletion.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1200,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    # Parse the JSON string from model
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: wrap content manually
        result = {"raw": content}
    return result
