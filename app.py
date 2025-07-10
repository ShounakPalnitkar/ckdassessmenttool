from flask import Flask, render_template, request, jsonify
import random
import os
from datetime import datetime

app = Flask(__name__)

# Risk calculation logic
def calculate_ckd_risk(form_data):
    risk_score = 0
    factors = []
    
    # Extract form data
    age = int(form_data.get('age', 0))
    sex = form_data.get('sex', '')
    race = form_data.get('race', '')
    hypertension = form_data.get('hypertension', 'no')
    diabetes = form_data.get('diabetes', 'no')
    duration = int(form_data.get('duration', 0))
    family_history = form_data.get('family_history', 'no')
    family_diseases = form_data.getlist('family_diseases')
    bmi = float(form_data.get('bmi', 0))
    smoking = form_data.get('smoking', 'never')
    cardiovascular = form_data.get('cardiovascular', 'no')
    symptoms = form_data.getlist('symptoms')
    
    # Calculate risk score
    # Age points
    if age >= 60:
        risk_score += 3
        factors.append(('Age (60+)', 3, 3, 'Demographics'))
    elif age >= 50:
        risk_score += 2
        factors.append(('Age (50-59)', 2, 3, 'Demographics'))
    elif age >= 40:
        risk_score += 1
        factors.append(('Age (40-49)', 1, 3, 'Demographics'))
    else:
        factors.append(('Age (<40)', 0, 3, 'Demographics'))
    
    # Race points
    if race == 'black':
        risk_score += 1
        factors.append(('African American', 1, 1, 'Demographics'))
    else:
        factors.append(('Race/ethnicity', 0, 1, 'Demographics'))
    
    # Hypertension points
    if hypertension == 'yes':
        risk_score += 2
        factors.append(('Hypertension', 2, 2, 'Medical Conditions'))
    elif hypertension == 'borderline':
        risk_score += 1
        factors.append(('Borderline hypertension', 1, 2, 'Medical Conditions'))
    else:
        factors.append(('No hypertension', 0, 2, 'Medical Conditions'))
    
    # Diabetes points
    if diabetes == 'type2':
        risk_score += 3
        factors.append(('Type 2 Diabetes', 3, 4, 'Medical Conditions'))
    elif diabetes == 'type1':
        risk_score += 4
        factors.append(('Type 1 Diabetes', 4, 4, 'Medical Conditions'))
    elif diabetes == 'prediabetes':
        risk_score += 1
        factors.append(('Prediabetes', 1, 4, 'Medical Conditions'))
    else:
        factors.append(('No diabetes', 0, 4, 'Medical Conditions'))
    
    # Diabetes duration points
    if duration >= 10:
        risk_score += 2
        factors.append(('Diabetes duration (10+ yrs)', 2, 2, 'Medical Conditions'))
    elif duration >= 5:
        risk_score += 1
        factors.append(('Diabetes duration (5-9 yrs)', 1, 2, 'Medical Conditions'))
    elif duration > 0:
        factors.append(('Diabetes duration (<5 yrs)', 0, 2, 'Medical Conditions'))
    
    # Family history points
    family_history_points = 0
    if family_history in ['parents', 'siblings']:
        family_history_points = 1
    elif family_history == 'both':
        family_history_points = 2
    
    risk_score += family_history_points
    family_diseases_text = ', '.join([
        {'ckd': 'Chronic Kidney Disease', 
         'diabetes': 'Diabetes', 
         'hypertension': 'Hypertension', 
         'heart': 'Heart Disease'}.get(d, d) 
        for d in family_diseases
    ])
    
    factors.append(('Family history', family_history_points, 2, 'Family History', 
                   f"({family_diseases_text})" if family_diseases_text else ''))
    
    # BMI points
    if bmi >= 30:
        risk_score += 1
        factors.append(('Obesity (BMI ≥30)', 1, 1, 'Lifestyle'))
    elif bmi >= 25:
        factors.append(('Overweight (BMI 25-29.9)', 0, 1, 'Lifestyle'))
    else:
        factors.append(('Normal weight', 0, 1, 'Lifestyle'))
    
    # Smoking points
    if smoking == 'current':
        risk_score += 1
        factors.append(('Current smoker', 1, 1, 'Lifestyle'))
    elif smoking == 'former':
        factors.append(('Former smoker', 0, 1, 'Lifestyle'))
    else:
        factors.append(('Never smoked', 0, 1, 'Lifestyle'))
    
    # Cardiovascular disease points
    if cardiovascular == 'yes':
        risk_score += 1
        factors.append(('Cardiovascular disease', 1, 1, 'Medical Conditions'))
    else:
        factors.append(('No cardiovascular disease', 0, 1, 'Medical Conditions'))
    
    # Symptoms points
    symptoms_count = len(symptoms)
    if symptoms_count >= 3:
        risk_score += 2
        factors.append(('Multiple symptoms', 2, 2, 'Symptoms'))
    elif symptoms_count >= 1:
        risk_score += 1
        factors.append(('Some symptoms', 1, 2, 'Symptoms'))
    else:
        factors.append(('No symptoms', 0, 2, 'Symptoms'))
    
    # Determine risk level
    if risk_score >= 10:
        risk_level = 'high'
        risk_percentage = '20-50%'
    elif risk_score >= 6:
        risk_level = 'moderate'
        risk_percentage = '5-20%'
    else:
        risk_level = 'low'
        risk_percentage = '<5%'
    
    # Check for urgent warning conditions
    has_pain = 'pain' in symptoms
    urgent_warning = (risk_score >= 12) or \
                    (diabetes == 'type1' and duration >= 10) or \
                    (symptoms_count >= 4) or \
                    has_pain
    
    # Prepare results
    result = {
        'risk_score': risk_score,
        'risk_level': risk_level,
        'risk_percentage': risk_percentage,
        'factors': factors,
        'age': age,
        'sex': sex,
        'race': race,
        'hypertension': hypertension,
        'diabetes': diabetes,
        'duration': duration,
        'family_history': family_history,
        'family_diseases': family_diseases,
        'family_diseases_text': family_diseases_text,
        'bmi': bmi,
        'smoking': smoking,
        'cardiovascular': cardiovascular,
        'symptoms_count': symptoms_count,
        'symptoms_list': symptoms,
        'has_pain': has_pain,
        'urgent_warning': urgent_warning,
        'watch_connected': False,  # Smartwatch connection not implemented in Flask
        'watch_data': None
    }
    
    return result

def generate_recommendations(result):
    recommendations = []
    
    # Age-based recommendations
    if result['age'] >= 60:
        recommendations.append({
            'title': "Age-Related Recommendations",
            'content': """<p>Since you're over 60, we recommend:</p>
            <ul>
                <li>Annual kidney function tests even without symptoms</li>
                <li>More frequent monitoring of blood pressure</li>
                <li>Regular check-ups with your primary care physician</li>
                <li>Hydration monitoring, especially in hot weather</li>
            </ul>"""
        })
    
    # Diabetes recommendations
    if result['diabetes'] != 'no':
        diabetes_type = {
            'type1': 'Type 1',
            'type2': 'Type 2',
            'prediabetes': 'Pre'
        }.get(result['diabetes'], '')
        
        content = f"<p>As you have {diabetes_type} diabetes:</p>"
        
        if result['diabetes'] in ['type1', 'type2']:
            content += """<ul>
                <li>Annual urine albumin test is crucial for early kidney damage detection</li>
                <li>Maintain A1C below 7% (individualized target based on your health status)</li>
                <li>Monitor blood sugar levels regularly</li>"""
            if result['duration'] >= 5:
                content += f"<li>Since you've had diabetes for {result['duration']} years, consider kidney function tests every 6 months</li>"
            content += """<li>Consult with an endocrinologist for optimal diabetes management</li>
                <li>Foot care and regular eye exams to prevent complications</li>
            </ul>"""
        else:
            content += """<ul>
                <li>Lifestyle changes can help prevent progression to diabetes</li>
                <li>Healthy diet with controlled carbohydrates</li>
                <li>Regular physical activity (150 minutes per week)</li>
                <li>Annual screening for diabetes development</li>
            </ul>"""
        
        recommendations.append({
            'title': "Diabetes Management",
            'content': content
        })
    
    # Add other recommendation categories similarly...
    # (Hypertension, Symptoms, Family History, etc.)
    
    # General lifestyle recommendations
    lifestyle_rec = {
        'title': "Lifestyle Recommendations",
        'content': """<ul>
            <li>Regular physical activity (150 mins/week moderate exercise):
                <ul>
                    <li>Walking, swimming, cycling</li>
                    <li>Strength training 2x/week</li>
                    <li>Consult doctor before starting new exercise program</li>
                </ul>
            </li>
            <li>Nutrition:
                <ul>
                    <li>Plant-based diet with lean proteins</li>
                    <li>Limit processed foods</li>
                    <li>Moderate protein intake (0.8g/kg body weight)</li>
                    <li>Increase fruits and vegetables</li>
                </ul>
            </li>
            <li>Other:
                <ul>
                    <li>Stay hydrated with water</li>
                    <li>Limit NSAID pain medication use</li>
                    <li>Moderate alcohol consumption</li>
                    <li>Stress reduction techniques</li>
                </ul>
            </li>
        </ul>"""
    }
    
    if result['smoking'] == 'current':
        lifestyle_rec['content'] = "<li>Smoking cessation is strongly recommended - consider nicotine replacement therapy or medications</li>" + lifestyle_rec['content']
    
    if result['bmi'] >= 25:
        lifestyle_rec['content'] = f"""<li>Weight management (current BMI {result['bmi']}):
            <ul>
                <li>Balanced diet with portion control</li>
                <li>Regular physical activity</li>
                <li>Behavioral modifications</li>
                <li>Consider consultation with dietitian</li>
            </ul>
        </li>""" + lifestyle_rec['content']
    
    recommendations.append(lifestyle_rec)
    
    return recommendations

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/assessment')
def assessment():
    return render_template('assessment.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    form_data = request.form
    result = calculate_ckd_risk(form_data)
    result['recommendations'] = generate_recommendations(result)
    return render_template('results.html', result=result)

@app.route('/download-report', methods=['POST'])
def download_report():
    result = request.json
    report_content = f"""Chronic Kidney Disease Risk Assessment Report
============================================

Risk Score: {result['risk_score']}/20
Risk Level: {result['risk_level'].upper()}
Estimated 5-year risk: {result['risk_percentage']}

Key Risk Factors:
----------------
{"\n".join([f"- {factor[0]}: {factor[1]}/{factor[2]} points" for factor in result['factors'] if factor[1] > 0])}

Recommendations:
---------------
{"\n\n".join([f"{rec['title']}\n{rec['content'].replace('<p>', '').replace('</p>', '').replace('<ul>', '').replace('</ul>', '').replace('<li>', '- ').replace('</li>', '')}" for rec in result['recommendations']])}

Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return jsonify({
        'content': report_content,
        'filename': f"ckd_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    })

if __name__ == '__main__':
    app.run(debug=True)
