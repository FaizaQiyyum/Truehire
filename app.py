from flask import Flask, render_template, request, session
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a random secret key

RULES = [
    ("no experience required", "Job postings claiming no experience required are often used to attract inexperienced candidates for scam roles."),
    ("earn money fast", "Promises of fast earnings are a common indicator of fraudulent job offers."),
    ("urgent hiring", "High-pressure urgent hiring language can signal scam postings trying to force quick decisions."),
    ("limited seats", "Limited seats or spots can be a manipulative tactic used by fake employers."),
    ("western union", "Requests for payment through Western Union or similar services are a strong red flag."),
    ("wire transfer", "Payment requests via wire transfer are a common scam pattern."),
    ("paypal", "Asking to receive or send payment through PayPal is suspicious in a job posting."),
    ("bank account", "Requests for bank account details indicate a risky or fraudulent posting."),
    ("unrealistic salary", "Unrealistically high salary claims are often used to lure candidates into scams."),
]

SALARY_PATTERN = re.compile(r"\$\s*\d{4,}")

CAREER_SUGGESTIONS = [
    (['security', 'cyber', 'network', 'infosec'], 'Cybersecurity Analyst'),
    (['data', 'analytics', 'machine learning', 'ai'], 'Data Analyst / AI Specialist'),
    (['design', 'ux', 'ui', 'creative'], 'UX / Product Designer'),
    (['marketing', 'content', 'social'], 'Digital Marketing Coordinator'),
    (['education', 'teaching', 'training', 'learning'], 'Learning Experience Designer'),
]


def analyze_job(description: str, company_name: str):
    text = description.strip()
    lowered = text.lower()
    reasons = []
    score = 0

    if not company_name.strip():
        reasons.append('Missing company name or employer information.')
        score += 20

    for phrase, reason in RULES:
        if phrase in lowered:
            reasons.append(reason)
            score += 15

    if SALARY_PATTERN.search(lowered) and ('per week' in lowered or 'per day' in lowered or 'weekly' in lowered or 'daily' in lowered):
        reasons.append('Salary claims with rapid payout frequency are often suspicious.')
        score += 10

    if 'unrealistic salary' in lowered or 'six figure' in lowered or '100k+' in lowered:
        reasons.append('Compensation claims are unusually high and may not match the job level.')
        score += 10

    score = max(0, min(score, 100))

    if score >= 60:
        risk = 'High'
    elif score >= 30:
        risk = 'Medium'
    else:
        risk = 'Low'

    if not reasons:
        reasons.append('No obvious fraud triggers found. Verify the employer and contact details before applying.')

    return {
        'risk': risk,
        'score': score,
        'reasons': reasons,
    }


def suggest_career(skills: str, interests: str):
    profile = f"{skills} {interests}".lower()
    for keywords, suggestion in CAREER_SUGGESTIONS:
        if any(keyword in profile for keyword in keywords):
            return suggestion
    return 'Professional Development Specialist'


@app.route('/', methods=['GET', 'POST'])
def index():
    analysis = None
    career_suggestion = None
    job_description = ''
    company_name = ''
    student_name = session.get('student_name', '')
    skills = session.get('skills', '')
    interests = session.get('interests', '')
    education = session.get('education', '')

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'analyze':
            job_description = request.form.get('job_description', '')
            company_name = request.form.get('company_name', '')
            analysis = analyze_job(job_description, company_name)
            # Store detection history
            if 'detection_history' not in session:
                session['detection_history'] = []
            session['detection_history'].append({
                'company_name': company_name,
                'job_description': job_description[:100] + '...' if len(job_description) > 100 else job_description,
                'risk': analysis['risk'],
                'score': analysis['score'],
                'date': '2026-04-16'  # Placeholder, could use datetime
            })
            session.modified = True
        elif form_type == 'profile':
            student_name = request.form.get('student_name', '')
            skills = request.form.get('skills', '')
            interests = request.form.get('interests', '')
            education = request.form.get('education', '')
            session['student_name'] = student_name
            session['skills'] = skills
            session['interests'] = interests
            session['education'] = education
            career_suggestion = suggest_career(skills, interests)
            session.modified = True

    return render_template(
        'index.html',
        analysis=analysis,
        career_suggestion=career_suggestion,
        job_description=job_description,
        company_name=company_name,
        student_name=student_name,
        skills=skills,
        interests=interests,
        education=education,
    )


@app.route('/profile')
def profile():
    student_name = session.get('student_name', '')
    skills = session.get('skills', '')
    interests = session.get('interests', '')
    education = session.get('education', '')
    detection_history = session.get('detection_history', [])
    career_suggestion = suggest_career(skills, interests) if skills or interests else None
    return render_template(
        'profile.html',
        student_name=student_name,
        skills=skills,
        interests=interests,
        education=education,
        career_suggestion=career_suggestion,
        detection_history=detection_history,
    )


if __name__ == '__main__':
    app.run(debug=True)
