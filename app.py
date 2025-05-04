import os
from flask import Flask, render_template, request, jsonify, url_for, redirect, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, RadioField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional
import sqlalchemy as sa
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# @article{zeng2022glm,
#   title={Glm-130b: An open bilingual pre-trained model},
#   author={Zeng, Aohan and Liu, Xiao and Du, Zhengxiao and Wang, Zihan and Lai, Hanyu and Ding, Ming and Yang, Zhuoyi and Xu, Yifan and Zheng, Wendi and Xia, Xiao and others},
#   journal={arXiv preprint arXiv:2210.02414},
#   year={2022}
# }

# Load model from local models folder
from modelscope.utils.constant import Tasks
from modelscope.pipelines import pipeline
from modelscope import Model
import torch.nn as nn

from modelscope import AutoTokenizer, AutoModel, snapshot_download

model_dir = "./models/ZhipuAI/chatglm3-6b"
tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
model = AutoModel.from_pretrained(model_dir, device_map="auto", offload_folder="offload_weights",
                                  trust_remote_code=True).half()

model = model.eval()


# Databse classes
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(15), default="Student")
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Student(User):
    __mapper_args__ = {
        'polymorphic_identity': 'student',
    }

    major = db.Column(db.String(100))
    year = db.Column(db.Integer)


class Admin(User):
    __mapper_args__ = {
        'polymorphic_identity': 'admin',
    }

    permissions = db.Column(db.String(200))


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User', backref='feedbacks')


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    user = db.relationship('User', backref='questions')


# Form classes
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(form, field):
        q = db.select(User).where(User.username == field.data)
        if db.session.scalar(q):
            raise ValidationError("Username already taken, please choose another")


class Calculate_BudgetForm(FlaskForm):
    accommodation = SelectField('Accommodation',
                                choices=[('None', 'None'), ('Dormitory', 'Dormitory'), ('Off-campus', 'Off-campus')],
                                validators=[DataRequired()])
    dormitory = SelectField('Select Dormitory',
                            choices=[('None', 'None'), ('elgar', 'Elgar Court'), ('maple', 'Maple Bank'),
                                     ('mason', 'Mason')],
                            validators=[Optional()])
    location = SelectField('Select Location',
                           choices=[('None', 'None'), ('nearby', 'Near School'), ('center', 'City Center'),
                                    ('fiveways', 'Fiveways')],
                           validators=[Optional()])
    food = SelectField('Food Preference', choices=[('cook', 'Cook Everyday'), ('rare_out', 'Eat Out 1-2 Times/Week'),
                                                   ('often_out', 'Eat Out 4-5 Times/Week'),
                                                   ('daily_out', 'Eat Out Daily')],
                       validators=[DataRequired()])
    transport_way = SelectField('Transport Preference',
                                choices=[('walk', 'Walk/Bike'), ('bus', 'Bus'), ('train', 'Train'),
                                         ('uber', 'Uber')], validators=[DataRequired()])
    supplies = SelectField('Supplies Preference', choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                           validators=[DataRequired()])
    submit = SubmitField('Calculate')


class Suggestion_BudgetForm(FlaskForm):
    budget_expression = StringField('Enter your budget (e.g. 500 + 300):', validators=[DataRequired()])
    time_unit = RadioField('Budget Time Unit',
                           choices=[('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')],
                           validators=[DataRequired()])

    # Optional preference fields
    prefer_accommodation = SelectField('Accommodation Preference',
                                       choices=[('', 'None'), ('Dormitory', 'Dormitory'), ('Off-campus', 'Off-campus')],
                                       validators=[Optional()])
    prefer_dormitory = SelectField('Preferred Dormitory',
                                   choices=[('', 'None'), ('elgar', 'Elgar Court'), ('maple', 'Maple Bank'),
                                            ('mason', 'Mason')], validators=[Optional()])
    prefer_rental = SelectField('Preferred Rental Area',
                                choices=[('', 'None'), ('nearby', 'Near School'), ('center', 'City Center'),
                                         ('fiveways', 'Fiveways')], validators=[Optional()])
    prefer_food = SelectField('Food Preference',
                              choices=[('', 'None'), ('cook', 'Cook Everyday'), ('rare_out', 'Eat Out 1-2 Times/Week'),
                                       ('often_out', 'Eat Out 4-5 Times/Week'), ('daily_out', 'Eat Out Daily')],
                              validators=[Optional()])
    prefer_supplies = SelectField('Supplies Preference',
                                  choices=[('', 'None'), ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
                                  validators=[Optional()])
    prefer_transport_ways = SelectField('Transport Preference',
                                        choices=[('', 'None'), ('walk', 'Walk/Bike'), ('bus', 'Bus'),
                                                 ('train', 'Train'),
                                                 ('uber', 'Uber')], validators=[Optional()])
    submit = SubmitField('Generate Suggestion')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return redirect(url_for('login'))


@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/chat_ui")
def chat_ui():
    return render_template("chat.html")


# AI chatbot
@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    chat_history = []
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if user_input:
            # Construct input and invoke the model
            response, chat_history = model.chat(tokenizer, user_input, chat_history)

            # Add to the display dialog list
            chat_history_display = [
                {'role': 'User', 'content': user_input},
                {'role': 'AI', 'content': response}
            ]
            return render_template('chat.html', chat_history=chat_history_display)
    return render_template('chat.html', chat_history=[])


UPLOAD_FOLDER = 'datas'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Feedback for AI section
@app.route('/feedback', methods=['POST'])
def feedback():
    feedback_text = request.form.get('feedback_text')
    if feedback_text:
        feedback_file = os.path.join(app.config['UPLOAD_FOLDER'], 'feedback.txt')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        with open(feedback_file, 'a', encoding='utf-8') as f:
            f.write(feedback_text + '\n')
        flash("Feedback received successfully", "success")
    return redirect(url_for('chat_ui'))


ACCESS_UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'txt', 'doc', 'docx', 'pdf'}

app.config['ACCESS_UPLOAD_FOLDER'] = ACCESS_UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your_secret_key'
os.makedirs(ACCESS_UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Section of Accessibility
@app.route('/accessibility', methods=['GET', 'POST'])
def accessibility():
    uploaded_files = os.listdir(app.config['ACCESS_UPLOAD_FOLDER'])  # List files in the folder

    # Function for accessibility feedback submission
    if request.method == 'POST' and 'feedback_text' in request.form:
        if current_user.role == 'Student':
            feedback_text = request.form['feedback_text']
            if feedback_text.strip():
                feedback = Feedback(user_id=current_user.id, content=feedback_text)
                db.session.add(feedback)
                db.session.commit()
                flash("Feedback submitted successfully.", "success")
            else:
                flash("Feedback submission failed", "fail")

    # Function for upload resources to accessibility section. Admin only function
    if request.method == 'POST' and 'file' in request.files:
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['ACCESS_UPLOAD_FOLDER'], filename))
            flash('Upload sucessfully！', 'success')
            uploaded_files = os.listdir(app.config['ACCESS_UPLOAD_FOLDER'])  # refresh
        else:
            flash("Upload failed: Unsupported file format！", "warning")

    # Handle search functionality
    search_query = request.args.get('search', '')
    if search_query:
        # Filter files based on search query (e.g., searching by filename)
        uploaded_files = [f for f in uploaded_files if search_query.lower() in f.lower()]

    feedbacks = []

    # Feedbacks for Admin to read
    if current_user.role == 'Admin':
        feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()

    return render_template('accessibility.html', files=uploaded_files, search_query=search_query,
                           feedbacks=feedbacks)


# Function for Admin to give responses to students' feedbacks. Admin only function
@app.route('/respond_feedback/<int:feedback_id>', methods=['POST'])
@login_required
def respond_feedback(feedback_id):
    if current_user.role in ['Student']:
        return redirect(url_for('accessibility'))

    feedback = Feedback.query.get(feedback_id)
    if feedback is None:
        flash("Feedback doesn't exist.", "fail")
    else:
        feedback.response = request.form['response']
        db.session.commit()
        flash("Response submitted", "success")
    return redirect(url_for('accessibility'))


# Download files from accessibility section
@app.route('/download/<filename>')
def download_file(filename):
    folder_path = os.path.abspath(app.config['ACCESS_UPLOAD_FOLDER'])
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        flash("File not found for download", "danger")
        return redirect(url_for('accessibility'))

    return send_from_directory(folder_path, filename, as_attachment=True)


# Delete files from accessibility section
@app.route('/delete/<filename>', methods=['GET'])
def delete_file(filename):
    file_path = os.path.join(app.config['ACCESS_UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"{filename} has been deleted.", "success")
    else:
        flash("File not found.", "fail")
    return redirect(url_for('accessibility'))


# Cost of living section
COSTS = {
    'dorm': {'elgar': 180, 'maple': 170, 'mason': 90},
    'rental': {'nearby': 250, 'center': 200, 'fiveways': 150},
    'food': {'cook': 25, 'rare_out': 50, 'often_out': 200, 'daily_out': 400},
    'supplies': {'low': 10, 'medium': 30, 'high': 70},
    'transport': {'walk': 0, 'bus': 30, 'train': 40, 'uber': 120}
}


# Navagation for section cost-of-living
@app.route('/cost_of_our_living')
def cost_of_our_living():
    resources = os.listdir(app.config['UPLOAD_RESOURCE_FOLDER'])  # resource folder for cost-of-living
    return render_template('cost_of_our_living.html', resources=resources)


# Calculate monthly cost
@app.route('/cost_of_living', methods=['GET', 'POST'])
def cost_of_living():
    total_budget = None
    if request.method == 'POST':
        # Get form data
        rent = float(request.form['rent'])
        groceries = float(request.form['groceries'])
        transportation = float(request.form['transportation'])
        entertainment = float(request.form['entertainment'])

        # Calculate total budget
        total_budget = rent + groceries + transportation + entertainment

    return render_template('cost_of_living.html', total_budget=total_budget)


# Calculate the budget of cost
@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    form = Calculate_BudgetForm()
    total = None

    if form.validate_on_submit():
        # flash
        if form.accommodation.data == 'None':
            flash("Please select an accommodation option.", "danger")
        elif form.accommodation.data == 'Dormitory' and form.dormitory.data == 'None':
            flash("Please select a dormitory.", "danger")
        elif form.accommodation.data == 'Off-campus' and form.location.data == 'None':
            flash("Please select a location for off-campus accommodation.", "danger")
        elif not form.food.data or not form.transport_way.data or not form.supplies.data:
            flash("Please fill in all required fields for food, transport, and supplies.", "danger")
        else:
            # calculate process
            try:
                if form.accommodation.data == 'Dormitory':
                    acc_cost = COSTS['dorm'][form.dormitory.data]
                else:
                    acc_cost = COSTS['rental'][form.location.data]

                food_cost = COSTS['food'][form.food.data]
                transport_cost = COSTS['transport'][form.transport_way.data]
                supplies_cost = COSTS['supplies'][form.supplies.data]

                total = acc_cost + food_cost + transport_cost + supplies_cost
            except Exception as e:
                flash("There was an error . Please try again.", "danger")

    return render_template('calculate.html', form=form, total=total)


# Function for students to generate and get their own budget suggestions
@app.route('/suggest', methods=['GET', 'POST'])
def suggest():
    form = Suggestion_BudgetForm()
    suggestion = None
    deficit = 0
    time_unit_value = None

    if form.validate_on_submit():
        # Protect correct input for the period time of budget
        try:
            budget_expression = form.budget_expression.data
            if not all(c in '0123456789+-*/(). ' for c in budget_expression):
                flash("Invalid characters in the budget expression. Please enter a valid expression.", "danger")
                return render_template('suggest.html', form=form)

            budget = eval(budget_expression)
            time_unit = form.time_unit.data
            time_unit_value = time_unit
            cost_multiplier = 1 if time_unit == 'weekly' else (52 / 12 if time_unit == 'monthly' else 52)

        except (ValueError, SyntaxError, ZeroDivisionError):
            flash("Invalid budget. Please enter a valid number or expression.", "danger")
            return render_template('suggest.html', form=form)

        comparison_budget = budget
        choices = {}

        if form.prefer_dormitory.data:
            acc_key = form.prefer_dormitory.data
            acc_cost = COSTS['dorm'][acc_key] * cost_multiplier
            choices['Accommodation'] = (acc_key.title(), acc_cost)
        elif form.prefer_rental.data:
            acc_key = form.prefer_rental.data
            acc_cost = COSTS['rental'][acc_key] * cost_multiplier
            choices['Accommodation'] = (acc_key.title(), acc_cost)
        else:
            acc_key = min(COSTS['dorm'], key=COSTS['dorm'].get)
            acc_cost = COSTS['dorm'][acc_key] * cost_multiplier
            choices['Accommodation'] = (acc_key.title(), acc_cost)

        food_key = form.prefer_food.data or min(COSTS['food'], key=COSTS['food'].get)
        supplies_key = form.prefer_supplies.data or min(COSTS['supplies'], key=COSTS['supplies'].get)
        transport_key = form.prefer_transport_ways.data or min(COSTS['transport'], key=COSTS['transport'].get)

        food_cost = COSTS['food'][food_key] * cost_multiplier
        supplies_cost = COSTS['supplies'][supplies_key] * cost_multiplier
        transport_cost = COSTS['transport'][transport_key] * cost_multiplier

        choices.update({
            'Food': (food_key.replace('_', ' ').title(), food_cost),
            'Supplies': (supplies_key.title(), supplies_cost),
            'Transport': (transport_key.title(), transport_cost)
        })

        total_cost = acc_cost + food_cost + supplies_cost + transport_cost

        if total_cost > comparison_budget:
            deficit = total_cost - comparison_budget
            flash(f"Budget deficit: £ {deficit:.2f} per {time_unit}. Consider cheaper options.", "warning")
        else:
            suggestion = choices
            flash("Here is your Budget plan suggestion!", "success")

    return render_template('suggest.html', form=form, suggestion=suggestion, deficit=deficit, time_unit=time_unit_value)


UPLOAD_RESOURCE_FOLDER = 'static/accommodation_resources'
app.config['UPLOAD_RESOURCE_FOLDER'] = UPLOAD_RESOURCE_FOLDER


# Function for upload cost-of-living resources
@app.route('/upload_resource', methods=['POST'])
def upload_resource():
    resources = os.listdir(app.config['UPLOAD_RESOURCE_FOLDER'])  # List files in the folder
    if request.method == 'POST':
        file = request.files.get('resource_file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_RESOURCE_FOLDER'], filename))
            flash(f"{filename} has been uploaded.", "success")
            resources = os.listdir(app.config['UPLOAD_RESOURCE_FOLDER'])  # refresh
        else:
            flash("Upload failed: Unsupported file format！", "warning")

    return render_template('cost_of_our_living.html', resources=resources)


# Download resources from cost-of-living section
@app.route('/download_resource/<filename>')
def download_resource(filename):
    folder_path = os.path.abspath(app.config['UPLOAD_RESOURCE_FOLDER'])
    file_path = os.path.join(folder_path, filename)

    if not os.path.exists(file_path):
        flash("File not found for download", "danger")
        return redirect(url_for('cost_of_our_living'))

    return send_from_directory(folder_path, filename, as_attachment=True)


# Delete resources form cost-of-living section. Admin only
@app.route('/delete_resource/<filename>', methods=['GET'])
def delete_resource(filename):
    file_path = os.path.join(app.config['UPLOAD_RESOURCE_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f"{filename} has been deleted.", "success")
    else:
        flash("File not found.", "fail")
    return redirect(url_for('cost_of_our_living'))


# Other functions in the system include accommodation and jobs and below is the navagation of other functions and the function of submitting questions to this section. Students only
@app.route('/other_functions', methods=['GET', 'POST'])
def other_functions():
    if request.method == 'POST' and 'question_text' in request.form:
        if current_user.role == 'Student':
            question_text = request.form['question_text']
            if question_text.strip():
                question = Question(user_id=current_user.id, content=question_text)
                db.session.add(question)
                db.session.commit()
                flash("Question submitted", "success")
            else:
                flash("Question submission failed", "fail")

    questions = []
    if current_user.role in ['Staff', 'Admin']:
        questions = Question.query.order_by(Question.timestamp.desc()).all()

    return render_template("other_functions.html")


# Route to handle dormitory search
@app.route('/search_dormitory', methods=['GET'])
def search_dormitory():
    search_query = request.args.get('search')
    # Dummy dormitory data, ideally you would query a database here
    dormitories = [
        {'name': 'Dorm A', 'price': 400, 'environment': 'Shared rooms, clean, good location', 'details_link': '#'},
        {'name': 'Dorm B', 'price': 500, 'environment': 'Private rooms, modern facilities', 'details_link': '#'}
    ]
    # Filter dormitories based on the search query (for simplicity, we're using basic substring match)
    filtered_dorms = [dorm for dorm in dormitories if
                      search_query.lower() in dorm['name'].lower() or search_query.lower() in dorm[
                          'environment'].lower()]
    return render_template('other_functions.html', dormitories=filtered_dorms)


# Route to handle campus job search
@app.route('/search_jobs', methods=['GET'])
def search_jobs():
    search_query = request.args.get('search')
    # Dummy job data, ideally you would query a database here
    jobs = [
        {'title': 'Student Assistant', 'description': 'Help with administrative tasks', 'details_link': '#'},
        {'title': 'Library Assistant', 'description': 'Work at the university library', 'details_link': '#'}
    ]
    filtered_jobs = [job for job in jobs if
                     search_query.lower() in job['title'].lower() or search_query.lower() in job['description'].lower()]
    return render_template('other_functions.html', jobs=filtered_jobs)


# Function for Admin to response students' questions
@app.route('/respond_question/<int:question_id>', methods=['POST'])
@login_required
def respond_question(question_id):
    if current_user.role == 'Student':
        flash("Unauthorized", "danger")
        return redirect(url_for('other_functions'))

    question = Question.query.get(question_id)
    if question:
        question.response = request.form.get('response', '').strip()
        db.session.commit()
        flash("Response submitted", "success")
    else:
        flash("Question doesn't exist.", "fail")

    return redirect(url_for('other_functions'))


# Login section
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


# Register Section
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You have logged in the system", "warning")
        return redirect(url_for('login'))
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Welcome to the system. You have registered the new account", "success")
        return redirect(url_for('login'))
    else:
        flash("Fail to register the new account!", "warning")

    return render_template('generic_form.html', title='Register', form=form)


# Feedback center for students to see the process of their feedbacks and questions
@app.route("/account")
@login_required
def account():
    feedbacks = Feedback.query.filter_by(user_id=current_user.id).order_by(Feedback.timestamp.desc()).all()
    questions = Question.query.filter_by(user_id=current_user.id).order_by(Question.timestamp.desc()).all()
    return render_template("account.html", feedbacks=feedbacks, questions=questions)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Database creation
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=6006)
