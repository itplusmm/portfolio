from flask import Flask, render_template, redirect, request, flash, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user, login_required, logout_user, LoginManager, login_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_key')
app.config['ENV'] = 'development'
app.config['DEBUG'] = True


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config['SQLALCHEMY_DATABASE_URI'] =\
           'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

upload_folder = os.path.join('static', 'upload')
os.makedirs(upload_folder, exist_ok=True)
app.config['UPLOAD_FOLDER'] = upload_folder

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

class Activity(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    desc = db.Column(db.String(500))
    image = db.Column(db.String(100))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Activity "{self.name}">'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    name = db.Column(db.String(100))
    image = db.Column(db.String(100))
    desc = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Blog "{self.name}">'

class Category(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    desc = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Category "{self.name}">'
    
class Vlog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    desc = db.Column(db.String(500))
    image = db.Column(db.String(500))
    video = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Vlog "{self.name}">'

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/blog")
def blog():

    rows = Blog.query.all()

    return render_template("blog.html", rows=rows)

@app.route("/about")
def about():

    return render_template("about.html")

@app.route("/activity")
def activity():

    rows = Activity.query.all()

    return render_template("act.html", rows=rows)

@app.route('/contact')
def contact():

    return render_template("contact.html")

@app.route('/vlog')
def vlog():

    rows = Vlog.query.all()

    return render_template("vlog.html", rows=rows)

@app.route('/view-activity')
def view_activity():

    rows = Activity.query.all()

    return render_template("view-act.html", rows=rows)

@app.route('/create-activity', methods=['GET', 'POST'])
def create_activity():

    rows = Activity.query.all()

    if request.method == "POST":

        name = request.form['name']
        desc = request.form['desc']
        image = request.files['image']

        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            image_filename = None

        act = Activity(name=name, desc=desc, image=image_filename)
        db.session.add(act)
        db.session.commit()
        flash("Activity added successfully", 'success')
        return redirect(url_for('view_activity'))
    
    return render_template("create-act.html", rows=rows)

@app.route('/view-blog')
def view_blog():

    rows = Blog.query.all()

    return render_template("view-blog.html", rows=rows)

@app.route('/create-blog', methods=['GET', 'POST'])
def create_blog():

    rows = Blog.query.all()

    if request.method == "POST":

        name = request.form['name']
        category = request.form['category']
        desc = request.form['desc']

        blog = Blog(name=name, category=category, desc=desc)
        db.session.add(blog)
        db.session.commit()
        flash("Blog added successfully", 'success')
        return redirect(url_for('view_blog'))

    return render_template("create-blog.html", rows=rows)

@app.route('/create_category', methods=['GET', 'POST'])
def create_category():

    rows = Category.query.all()

    if request.method == "POST":

        name = request.form['name']
        desc = request.form['desc']
        category = Category(name=name, desc=desc)
        db.session.add(category)
        db.session.commit()
        flash("Category added successfully", 'success')
        return redirect(url_for('view_category'))

    return render_template("create_category.html", rows=rows)

@app.route('/create-vlog', methods=['GET', 'POST'])
def create_vlog():

    rows = Vlog.query.all()

    if request.method == "POST":

        name = request.form['name']
        desc = request.form['desc']
        image = request.files['image']

        if image and allowed_file(image.filename):
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            image_filename = None

        video = request.form['video']

        vlog = Vlog(name=name, desc=desc, image=image_filename, video=video)
        db.session.add(vlog)
        db.session.commit()
        flash("Category added successfully", 'success')
        return redirect(url_for('view_vlog'))
    
    return render_template("create-vlog.html", rows=rows)

@app.route('/view-vlog', methods=['GET', 'POST'])
def view_vlog():

    rows = Vlog.query.all()

    return render_template("view-vlog.html", rows=rows)

@app.route('/delete_category/<int:category_id>', methods=['GET', 'POST'])
def delete_category(category_id):
    category = Category.query.get(category_id)

    if category is None:
        abort(404)

    db.session.delete(category)
    db.session.commit()

    flash(f"Category {category.name} has been deleted.", 'success')
    return redirect(url_for('view_category'))

@app.route('/delete_activity/<int:activity_id>', methods=['GET', 'POST'])
def delete_activity(activity_id):

    activity = Activity.query.get(activity_id)

    if activity is None:
        abort(404)

    db.session.delete(activity)
    db.session.commit()

    flash(f"Activity {activity.name} has been deleted.", 'success')
    return redirect(url_for('view_activity'))

@app.route('/delete_blog/<int:blog_id>', methods=['GET', 'POST'])
def delete_blog(blog_id):

    blog = Blog.query.get(blog_id)

    if blog is None:
        abort(404)

    db.session.delete(blog)
    db.session.commit()

    flash(f"Blog {blog.name} has been deleted.", 'success')
    return redirect(url_for('view_blog'))

@app.route('/delete_vlog/<int:vlog_id>', methods=['GET', 'POST'])
def delete_vlog(vlog_id):

    vlog = Vlog.query.get(vlog_id)

    if vlog is None:
        abort(404)

    db.session.delete(vlog)
    db.session.commit()

    flash(f"Vlog {vlog.name} has been deleted.", "sucess")
    return redirect(url_for('view_vlog'))

@app.route('/view_category')
def view_category():

    rows = Category.query.all()

    return render_template("view_category.html", rows=rows)

if __name__=='__main__': 
   app.run(debug=True)