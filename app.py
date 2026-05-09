import os
import numpy as np
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'digital_kidney_twin_v22_final'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'kidney_twin.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- LEXIQUE DE TRADUCTION SYNCHRONISÉ ---
LEXICON = {
    'en': {
        'platform_name': 'DIGITAL KIDNEY TWIN',
        'hero_msg': 'Every stage you ignore… silently brings you closer to the end.',
        'discover_btn': 'Discover your pathology',
        'dash': 'Dashboard', 'add_pt': 'Add Patient', 'open_twin': 'Open Twin',
        'delete': 'Delete', 'save': 'Sync & Save Results', 'mandatory': 'Mandatory Data',
        'optional': 'Optional Data', 'date': 'Check Date', 'predict': '3-Month Prediction',
        'history': 'History', 'back': 'Back', 'name': 'Full Name', 'age': 'Age',
        'weight': 'Weight', 'gender': 'Gender', 'male': 'Male', 'female': 'Female',
        'conc': 'Urine Concentration', 'conc_high': 'High', 'conc_med': 'Medium', 'conc_low': 'Low',
        'cr': 'Creatinine', 'alb': 'Albumin', 'what_if': 'What if I drank more water?',
        'back_sim': 'Return to reality', 'ai_advice': 'AI Clinical Advice', 'stage': 'STAGE',
        'current_cond': 'Current Condition', 'sim_water': 'Simulation: High Water',
        'smoker': 'Smoker?', 'yes': 'Yes', 'no': 'No', 'next': 'Continue',
        'heart': 'Heart Disease', 'family': 'Family History', 'diabetes': 'Diabetes', 'htn': 'Hypertension',
        'confirm_del': 'Delete patient?', 'developed_by': 'Developed by Oulmi Manar & Rouabah Chaima'
    },
    'fr': {
        'platform_name': 'DIGITAL KIDNEY TWIN',
        'hero_msg': 'Chaque étape que vous ignorez… vous rapproche silencieusement de la fin.',
        'discover_btn': 'Découvrez votre pathologie',
        'dash': 'Tableau de bord', 'add_pt': 'Ajouter Patient', 'open_twin': 'Ouvrir Twin',
        'delete': 'Supprimer', 'save': 'Enregistrer les résultats', 'mandatory': 'Obligatoire',
        'optional': 'Optionnel', 'date': "Date de l'examen", 'predict': 'Prédiction (3 mois)',
        'history': 'Historique', 'back': 'Retour', 'name': 'Nom complet', 'age': 'Âge',
        'weight': 'Poids', 'gender': 'Sexe', 'male': 'Homme', 'female': 'Femme',
        'conc': "Concentration de l'urine", 'conc_high': 'Élevée', 'conc_med': 'Moyenne', 'conc_low': 'Faible',
        'cr': 'Créatinine', 'alb': 'Albumine', 'what_if': "Et si je buvais plus d'eau ?",
        'back_sim': 'Retour à l\'état actuel', 'ai_advice': 'Conseils Cliniques IA', 'stage': 'STADE',
        'current_cond': 'État Actuel', 'sim_water': 'Simulation : Apport en eau +',
        'smoker': 'Fumeur ?', 'yes': 'Oui', 'no': 'Non', 'next': 'Continuer',
        'heart': 'Maladies Cardiaques', 'family': 'Antécédents Familiaux', 'diabetes': 'Diabète', 'htn': 'Hypertension',
        'confirm_del': 'Supprimer le patient ?', 'developed_by': 'Développé par Oulmi Manar & Rouabah Chaima'
    },
    'ar': {
        'platform_name': 'تـوأم الـكـلـى الـرقـمـي',
        'hero_msg': 'كل مرحلة تتجاهلها... تقربك بصمت من النهاية.',
        'discover_btn': 'اكتشف حالتك المرضية',
        'dash': 'لوحة التحكم', 'add_pt': 'إضافة مريض', 'open_twin': 'فتح التوأم',
        'delete': 'حذف', 'save': 'حفظ ومزامنة النتائج', 'mandatory': 'بيانات إجبارية',
        'optional': 'بيانات اختيارية', 'date': 'تاريخ الفحص', 'predict': 'توقعات (3 أشهر)',
        'history': 'السجل', 'back': 'رجوع', 'name': 'الاسم الكامل', 'age': 'العمر',
        'weight': 'الوزن', 'gender': 'الجنس', 'male': 'ذكر', 'female': 'أنثى',
        'conc': 'تركيز البول', 'conc_high': 'مرتفع', 'conc_med': 'متوسط', 'conc_low': 'منخفض',
        'cr': 'كرياتينين', 'alb': 'ألبومين', 'what_if': 'ماذا لو شربت المزيد من الماء؟',
        'back_sim': 'العودة للحالة الحالية', 'ai_advice': 'توصيات الذكاء الاصطناعي', 'stage': 'المرحلة',
        'current_cond': 'الحالة الحالية', 'sim_water': 'محاكاة: زيادة شرب الماء',
        'smoker': 'مدخن؟', 'yes': 'نعم', 'no': 'لا', 'next': 'استمرار',
        'heart': 'أمراض القلب', 'family': 'تاريخ عائلي', 'diabetes': 'سكري', 'htn': 'ضغط دم',
        'confirm_del': 'حذف المريض؟', 'developed_by': 'تطوير: أولمي منار و روابح شيماء'
    }
}

# --- MODÈLES ---
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    gender = db.Column(db.String(10))
    is_smoker = db.Column(db.Boolean)
    has_diabetes = db.Column(db.Boolean)
    has_heart_disease = db.Column(db.Boolean)
    records = db.relationship('HealthRecord', backref='patient', cascade="all, delete-orphan", lazy=True)

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    creatinine = db.Column(db.Float)
    albumin = db.Column(db.Float)
    egfr = db.Column(db.Float)
    urine_concentration = db.Column(db.String(20))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))

def calculate_egfr(cr, age, gender):
    if cr <= 0:
        return 0
    k = 0.7 if gender.lower() == 'female' else 0.9
    a = -0.241 if gender.lower() == 'female' else -0.302
    gm = 1.012 if gender.lower() == 'female' else 1.0
    return round(142 * (min(cr/k, 1)**a) * (max(cr/k, 1)**-1.2) * (0.9938**age) * gm, 1)

@app.context_processor
def inject_vars():
    l = session.get('lang', 'fr')
    return dict(text=LEXICON[l], lang=l, rtl=(l == 'ar'), now=datetime.utcnow())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', patients=Patient.query.all())

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/set_lang/<l>')
def set_lang(l):
    session['lang'] = l
    return redirect(request.referrer or url_for('index'))

@app.route('/add_patient', methods=['POST'])
def add_patient():
    p = Patient(
        name=request.form.get('name'),
        age=int(request.form.get('age')),
        weight=float(request.form.get('weight')),
        gender=request.form.get('gender'),
        is_smoker=(request.form.get('smoker') == 'true'),
        has_diabetes='diabetes' in request.form,
        has_heart_disease='heart' in request.form
    )
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('patient_detail', id=p.id))

@app.route('/patient/<int:id>')
def patient_detail(id):
    p = Patient.query.get_or_404(id)
    recs = sorted(p.records, key=lambda x: x.date)
    latest = recs[-1] if recs else None
    stage = 1
    color = "#1e293b"
    
    if latest:
        if latest.egfr >= 90:
            stage, color = 1, "#10b981"
        elif latest.egfr >= 60:
            stage, color = 2, "#facc15"
        elif latest.egfr >= 30:
            stage, color = 3, "#f97316"
        elif latest.egfr >= 15:
            stage, color = 4, "#ef4444"
        else:
            stage, color = 5, "#7f1d1d"
    
    pred_val = None
    if len(recs) >= 2:
        pred_val = round(recs[-1].egfr - 2, 1)
    
    return render_template('patient_detail.html', p=p, records=recs, latest=latest, stage=stage, color=color, pred_val=pred_val)

@app.route('/add_record/<int:p_id>', methods=['POST'])
def add_record(p_id):
    p = Patient.query.get_or_404(p_id)
    cr = float(request.form.get('creatinine'))
    alb = float(request.form.get('albumin'))
    dt = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    
    db.session.add(HealthRecord(
        date=dt,
        creatinine=cr,
        albumin=alb,
        egfr=calculate_egfr(cr, p.age, p.gender),
        urine_concentration=request.form.get('urine_concentration'),
        patient_id=p.id
    ))
    db.session.commit()
    return redirect(url_for('patient_detail', id=p_id))

@app.route('/delete_patient/<int:id>', methods=['POST'])
def delete_patient(id):
    p = Patient.query.get(id)
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('dashboard'))

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=False)