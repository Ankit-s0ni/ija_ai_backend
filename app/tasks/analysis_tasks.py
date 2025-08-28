from app.core.celery_app import celery_app
import openai
import json

# Config and API key init
from app.core.config import settings

# Initialize Gemini API Key
openai.api_key = settings.GEMINI_API_KEY

@celery_app.task(name="generate_analysis")
def generate_analysis(resume_data: dict, job_description: str, experience_level: str) -> dict:
    # Prompt from frontend geminiService
    prompt = f"""
You are an expert career coach and resume analyst with years of experience helping candidates at all levels (from fresher to senior) land jobs at top tech companies.

Your task is to provide a detailed, objective analysis of the provided RESUME.
The candidate has specified their experience level as: **{experience_level.upper()}**. All of your feedback must be tailored to the expectations for this level.

This is a TARGETED analysis. You must provide a tailoring score and keyword analysis.

Your analysis must be critical, constructive, and strictly follow the provided JSON schema. Do not include any introductory text or markdown formatting.

{json.dumps(resume_data)}

{job_description}
"""
    response = openai.ChatCompletion.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.7,
    )
    content = response.choices[0].message.content
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {"raw": content}
    return result
