from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://workingblog:workingblog@localhost:8889/workingblog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'f8wv3w2f>v9j4sEuhcNYydAGMzzZJgkGgyHE9gUqaJcCk^f*^o7fQyBT%XtTvcYM'


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    entry = db.relationship('Entry', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


class Entry(db.Model):
   
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))
    created = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user ):
        self.title = title
        self.body = body
        self.created = datetime.utcnow()
        self.user = user

    def is_valid(self):
        
        if self.title and self.body and self.created:
            return True
        else:
            return False


@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        task_name = request.form['task']   
        new_task = Task(task_name, owner)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False,owner=owner).all()
    completed_tasks = Task.query.filter_by(completed=True,owner=owner).all()
    return render_template('singleUser.html', title="Your entries", 
        tasks=tasks, completed_tasks=completed_tasks)   
    

@app.route("/blog")
def display_blog_entries():
   
    entry_id = request.args.get('id')
    if (entry_id):
        entry = Entry.query.get(entry_id)
        return render_template('single_entry.html', title="Blog Entry", entry=entry)

    
    sort = request.args.get('sort')
    if (sort=="newest"):
        all_entries = Entry.query.order_by(Entry.created.desc()).all()
    else:
        all_entries = Entry.query.all()   
    return render_template('all_entries.html', title="All Entries", all_entries=all_entries)


@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    
    if request.method == 'POST':
        new_entry_title = request.form['title']
        new_entry_body = request.form['body']
        new_entry = Entry(new_entry_title, new_entry_body)

        if new_entry.is_valid():
            db.session.add(new_entry)
            db.session.commit()

            
            url = "/blog?id=" + str(new_entry.id)
            return redirect(url)
        else:
            flash("Please check your entry for errors. Both a title and a body are required.")
            return render_template('new_entry_form.html',
                title="Create new blog entry",
                new_entry_title=new_entry_title,
                new_entry_body=new_entry_body)

    else: 
        return render_template('new_entry_form.html', title="Create new blog entry")

if __name__ == '__main__':
    app.run()