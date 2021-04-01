from flask import Flask, url_for, render_template, redirect, flash, request, session, send_from_directory, current_app
from passlib.hash import sha256_crypt
from flask_sqlalchemy import SQLAlchemy
import secrets
from sqlalchemy.dialects.mysql import TEXT
from datetime import datetime
import os
from flask_msearch import Search
from functools import wraps
from tkinter import *
from tkinter import messagebox
from sqlalchemy.exc import IntegrityError


# app configuration 
app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(username='roots',
#                                         password='root', hostname='localhost', databasename='mydbs')
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///sqlite3.db'
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.update(
    #Set the secret key to a sufficiently random value
    SECRET_KEY=os.urandom(24)
)

# initialise the cursor
db = SQLAlchemy(app)
search = Search()
search.init_app(app)

# initialise the tkinter
# window =  Tk()
# window.eval('tk::PlaceWindow %s center' % window.winfo_toplevel() )
# window.withdraw()


# the users table
class Blog_user(db.Model):
    __tablename__ = "blog_user"
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    username = db.Column("username", db.String(100),
                        nullable=False, unique=True)
    password = db.Column("password", db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey(
                    'tag.id'), primary_key=True),
                db.Column('article_id', db.Integer, db.ForeignKey(
                    'article.id'), primary_key=True)
                )


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name


# the users table
class Article(db.Model):
    __tablename__ = "article"
    __searchable__ = ['title', 'author', 'category']
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    image = db.Column("image", db.String(250), default="image.jpg")
    title = db.Column("title", db.String(255), nullable=False)
    author = db.Column("author", db.String(100), nullable=False)
    body = db.Column("body", TEXT, nullable=False)
    comments = db.Column("comments", db.Integer, default=0)
    views = db.Column("views", db.Integer, default=0)
    category = db.Column("category", db.String(50), default="general")
    comment = db.relationship('Comment', lazy="subquery",
                            backref=db.backref('article', lazy="joined"))
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
                        backref=db.backref('blogs_associated', lazy="dynamic"))
    date_created = db.Column("date_created", db.DateTime, nullable=False,
                            default=datetime.utcnow)

    def __init__(self, image, title, author, body, category):
        self.image = image
        self.title = title
        self.author = author
        self.body = body
        self.category = category


# the comment section
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    author = db.Column("author", db.String(100), nullable=False, unique=False)
    email = db.Column('email', db.String(100), nullable=False, unique=False)
    message = db.Column("message", TEXT, nullable=False, unique=False)
    article_id = db.Column("article_id", db.Integer,
                        db.ForeignKey("article.id"), nullable=False)
    pub_date = db.Column("pub_date", db.DateTime, nullable=False,
                        default=datetime.utcnow)
    status = db.Column('status', db.Boolean, default=False)
    

    def __init__(self, author, email, message, article_id):
        self.author = author
        self.email = email
        self.message = message
        self.article_id = article_id


# the newsletter emails
class Newsletter(db.Model):
    __tablename__ = "newsletter"
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    email = db.Column("email", db.String(100), nullable=False, unique=True)


    def __init__(self, email):
        self.email = email


# the alumni forum table
class Forum(db.Model):
    __tablename__ = "forum"
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    username = db.Column("username", db.String(100),
                        nullable=False, unique=False)
    email = db.Column("email", db.String(100), nullable=False, unique=False)
    message = db.Column("message", TEXT, nullable=False, unique=False)
    pub_date = db.Column("pub_date", db.DateTime, nullable=False,
                        default=datetime.utcnow)

    def __init__(self, username, email, message):
        self.username = username
        self.email = email
        self.message = message


# the alumni users table
class User(db.Model):
    __tablename__ = "user"
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    name = db.Column("name", db.String(100), nullable=False)
    email = db.Column("email", db.String(100), nullable=False)
    username = db.Column("username", db.String(100),
                        nullable=False, unique=True)
    password = db.Column("password", db.String(100), nullable=False)
    date_reg = db.Column("date_reg", db.DateTime, nullable=False,
                        default=datetime.utcnow)

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password


# the alumni blog users table
class Alumni_blog_user(db.Model):
    __tablename__ = "alumni_blog_user"
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    username = db.Column("username", db.String(100),
                        nullable=False, unique=True)
    password = db.Column("password", db.String(100), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password


# the simple tag table for alumni
a_tags = db.Table('a_tags',
                db.Column('a_tag_id', db.Integer, db.ForeignKey(
                    'a_tag.id'), primary_key=True),
                db.Column('alumni_article_id', db.Integer, db.ForeignKey(
                    'alumni_article.id'), primary_key=True)
                )


# the tag table for the alumni 
class A_tag(db.Model):
    __tablename__ = "a_tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name


# the users table
class Alumni_article(db.Model):
    __tablename__ = "alumni_article"
    __searchable__ = ['title', 'author', 'category']
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    image = db.Column("image", db.String(250), default="image.jpg")
    title = db.Column("title", db.String(255), nullable=False)
    author = db.Column("author", db.String(100), nullable=False)
    body = db.Column("body", TEXT, nullable=False)
    comments = db.Column("comments", db.Integer, default=0)
    views = db.Column("views", db.Integer, default=0)
    category = db.Column("category", db.String(50), default="general")
    comment = db.relationship('Alumni_comment', lazy="subquery",
                            backref=db.backref('alumni_article', lazy="joined"))
    a_tags = db.relationship('A_tag', secondary=a_tags, lazy='subquery',
                        backref=db.backref('blogs_associated', lazy="dynamic"))
    date_created = db.Column("date_created", db.DateTime, nullable=False,
                            default=datetime.utcnow)

    def __init__(self, image, title, author, body, category):
        self.image = image
        self.title = title
        self.author = author
        self.body = body
        self.category = category


# the alumni comment section
class Alumni_comment(db.Model):
    __tablename__ = "alumni_comment"
    id = db.Column("id", db.Integer, primary_key=True, nullable=False)
    author = db.Column("author", db.String(100), nullable=False, unique=False)
    email = db.Column('email', db.String(100), nullable=False, unique=False)
    message = db.Column("message", TEXT, nullable=False, unique=False)
    alumni_article_id = db.Column("alumni_article_id", db.Integer,
                        db.ForeignKey("alumni_article.id"), nullable=False)
    pub_date = db.Column("pub_date", db.DateTime, nullable=False,
                        default=datetime.utcnow)
    status = db.Column('status', db.Boolean, default=False)

    def __init__(self, author, email, message, alumni_article_id):
        self.author = author
        self.email = email
        self.message = message
        self.alumni_article_id = alumni_article_id


# Check if user is logged in
def logged_in(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorised, Please Login", "danger")
            return redirect(url_for("alumni_login"))
    return wrapper


# Check if user is logged in
def logged_ins(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorised, Please Login", "danger")
            return redirect(url_for("alumniblog_login"))
    return wrapper



# Check if admin is logged in
def is_logged_in(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorised, Please Login", "danger")
            return redirect(url_for("admin_login"))
    return wrapper


# messagebox.showinfo('Alert', 'Unauthorised, Please Login')
# window.deiconify()
# window.destroy()
# window.quit()

# # upload image configuration
# UPLOAD_FOLDER = '/static/blog_img'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def save_images(photo):
    hash_photo = secrets.token_urlsafe(10)
    _, file_extension = os.path.splitext(photo.filename)
    photo_name = hash_photo + file_extension
    file_path = os.path.join(current_app.root_path,
                            "static/blog_img", photo_name)
    photo.save(file_path)
    return photo_name


def save_image(photo):
    hash_photo = secrets.token_urlsafe(10)
    _, file_extension = os.path.splitext(photo.filename)
    photo_name = hash_photo + file_extension
    file_path = os.path.join(current_app.root_path,
                            "static/a_blog_img", photo_name)
    photo.save(file_path)
    return photo_name


# user1 = Blog_user(username="admin", password=sha256_crypt.hash(str("admin")))


# the index page
@app.route('/')
def index():
    return render_template("main/index.htm")


# the footer
@app.route('/footer', methods=["POST", "GET"])
def footer():
    if request.method == "POST":
        email = request.form['email']
        new = Newsletter(email)
        results = Newsletter.query.filter_by(email=email).first()
        if results:
            flash("You have subscribe already", "danger")
            return redirect(url_for('index'))   
        else:
            db.session.add(new)
            db.session.commit()
            return redirect(url_for('index'))  
    return redirect(url_for('index'))  


# the executives page
@app.route('/executives')
def executives():
    return render_template("main/executives.htm")


# the about page
@app.route('/about')
def about():
    return render_template("main/about.htm")


# the gallery page
@app.route('/gallery')
def gallery():
    return render_template("main/gallery.htm")


# the event page
@app.route('/event')
def event():
    return render_template("main/event.htm")


# admin register
@app.route('/admin_reg', methods=["POST", "GET"])
def admin_reg():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash('Enter all fields', 'danger')
        else:
            user = Blog_user(username, sha256_crypt.hash(password))
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully', 'success')
            return redirect(url_for('admin_login'))

    return render_template('admin/admin_reg.htm')


# admin login
@app.route('/admin_login', methods=["POST", "GET"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash("Enter all fields", "danger")
        else:
            results = Blog_user.query.filter_by(username=username).first()
            if results:
                result = results.password
                if sha256_crypt.verify(password, result):
                    # passed
                    session["logged_in"] = True
                    session["username"] = username
                    session["password"] = password
                    flash("You are now logged in.", "success")
                    return redirect(url_for("dashboard"))
                elif not sha256_crypt.verify(password, result):
                    flash("Invalid Password", "danger")
                    return render_template('admin/admin_login.htm')
            else:
                error = "This username does not exist"
                return render_template("admin/admin_login.htm", error=error)
    return render_template("admin/admin_login.htm")


# the blog dashboard
@app.route('/dashboard', methods=["POST", "GET"])
@is_logged_in
def dashboard():
    results = db.engine.execute("SELECT * FROM article")
    arts = Article.query.order_by(Article.date_created.desc()).all()
    if results:
        return render_template("admin/dashboard.htm", arts=arts)
    else:
        msg = "No articles found"
        return render_template("admin/dashboard.htm", msg=msg)


# the articles page
@app.route("/articles", methods=["POST", "GET"])
def articles():
    results = db.engine.execute("SELECT * FROM article")
    articles = Article.query.order_by(Article.date_created.desc()).all()

    if results:
        # image_names = os.listdir('./static/blog_img')
        tags = Tag.query.all()
        return render_template("admin/articles.htm", articles=articles, tags=tags)
    else:
        msg = "No articles found"
        return render_template("admin/articles.htm", msg=msg)


@app.route("/search")
def search():
    keyword = request.args.get('keyword')
    articles = Article.query.msearch(keyword, fields=['title', 'author', 'category'], limit=20).all()
    tags = Tag.query.all()
    
    return render_template("admin/articles.htm", articles=articles, tags=tags, keyword=keyword)


@app.route("/tag/<string:name>", methods=["POST", "GET"])
def article_tag(name):
    # results = db.engine.execute('SELECT article_id FROM tags WHERE tag_id = %s',[id])

    articles = Article.query.filter_by(category=name).all()

    return render_template("admin/article_tag.htm", articles=articles)


# the article page
@app.route("/article/<string:id>/", methods=["POST", "GET"])
def article(id):
    article = Article.query.filter_by(id=id).first()
    articles = Article.query.order_by(Article.date_created.desc()).all()
    comments = Comment.query.filter_by(article_id=id).all()
    tags = Tag.query.all()
    article.views += 1
    db.session.commit()

    if request.method == "POST":
        author = request.form["author"]
        email = request.form["email"]
        message = request.form['message']
        comment = Comment(author, email, message, id,)
        db.session.add(comment)
        article.comments += 1
        flash("Your comment has been submited", "success")
        db.session.commit()
        return redirect(request.url)

    return render_template("admin/article.htm", comments=comments, article=article, articles=articles, tags=tags)


@app.route("/add_article", methods=["POST", "GET"])
@is_logged_in
def add_article():
    if request.method == "POST":
        photo = save_images(request.files["photo"])
        # photo = request.files["photo"]
        title = request.form["title"]
        author = request.form['author']
        body = request.form["body"]
        category = request.form["tags"]
        if not body or not title or not photo or not category or not author:
            flash("Enter all fields", "danger")
        else:
            art = Article(
                photo, title, author, body, category)
            tag = request.form["tags"]
            present_tag = Tag.query.filter_by(name=tag).first()
            if(present_tag):
                present_tag.blogs_associated.append(art)
            else:
                new_tag = Tag(name=tag)
                new_tag.blogs_associated.append(art)
                db.session.add(new_tag)

            db.session.add(art)
            db.session.commit()
            flash("Article Created", "success")
            return redirect(url_for("dashboard"))

    return render_template("admin/add_article.htm")


# the url that's send the image 
@app.route("/add_article/<filename>")
def send_image(filename):
    return send_from_directory("./static/blog_img", filename)


# the edit article function
@app.route("/edit_article/<string:id>", methods=["POST", "GET"])
@is_logged_in
def edit_article(id):
    article = Article.query.filter_by(id=id).first()
    # populate the data
    article_title = article.title
    article_body = article.body
    article_image = article.image
    article_author = article.author
    article_category = article.category
    if request.method == "POST":
        title = request.form["title"]
        author = request.form['author']
        body = request.form["body"]
        category = request.form["tags"]
        if not body or not title or not author or not category:
            flash("Enter all fields", "danger")
        else:
            article = Article.query.filter_by(id=id).first()
            article.title = title
            article.username = author
            article.body = body
            article.category = category
            db.session.commit()
            flash("Article Updated", "success")
            return redirect(url_for("dashboard"))

    return render_template("admin/edit_article.htm", article_title=article_title, article_category=article_category,
                        article_body=article_body, article_image=article_image, article_author=article_author)


@app.route("/delete_article/<string:id>", methods=["POST"])
@is_logged_in
def delete_article(id):
    article = Article.query.filter_by(id=id).first()
    db.session.delete(article)
    db.session.commit()
    flash("Article Deleted", "success")
    return redirect(url_for("dashboard"))


@app.route('/alumni_reg', methods=["POST", "GET"])
def alumni_reg():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form['confirm_password']
        if not name or not email or not username or not password or not confirm_password:
            flash("Enter all fields", "danger")
        else:
            try:
                # creating an instance of User
                users = User(name, email, username,
                            sha256_crypt.hash(str(password)))
                if password == confirm_password:
                    # committing to the database
                    db.session.add(users)
                    db.session.commit()
                    flash("You have successfully registered", "success")
                    return redirect(url_for("alumni_login"))
                else:
                    error = "Password do not match"
                    return render_template("alumni/alumni_reg.htm", error=error)
            except IntegrityError:
                db.session.rollback()
                flash(
                    "ERROR! There was an error in registering, try again later", "danger")
    return render_template("alumni/alumni_reg.htm")


# admin login
@app.route('/alumni_login', methods=["POST", "GET"])
def alumni_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash("Enter all fields", "danger")
        else:
            results = User.query.filter_by(username=username).first()
            if results:
                result = results.password
                if sha256_crypt.verify(password, result):
                    # passed
                    session["logged_in"] = True
                    session["username"] = username
                    session["password"] = password
                    flash("You are now logged in.", "success")
                    return redirect(url_for("alumni_index"))
                elif not sha256_crypt.verify(password, result):
                    flash("Invalid Password", "danger")
                    return render_template('alumni/alumni_login.htm')
            else:
                error = "This username does not exist"
                return render_template("alumni/alumni_login.htm", error=error)
    return render_template("alumni/alumni_login.htm")


# the alumni dashboard
@app.route('/alumni_index', methods=["POST", "GET"])
@logged_in
def alumni_index():
    return render_template("alumni/alumni_index.htm")


# the alumni about page
@app.route('/alumni_about', methods=["POST", "GET"])
@logged_in
def alumni_about():
    return render_template("alumni/alumni_about.htm")


# alumni blog register
@app.route('/alumniblog_reg', methods=["POST", "GET"])
def alumniblog_reg():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash('Enter all fields', 'danger')
        else:
            user = Alumni_blog_user(username, sha256_crypt.hash(password))
            db.session.add(user)
            db.session.commit()
            flash('User registered successfully', 'success')
            return redirect(url_for('alumniblog_login'))

    return render_template('alumni/alumniblog_reg.htm')


# alumni blog login
@app.route('/alumniblog_login', methods=["POST", "GET"])
def alumniblog_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not username or not password:
            flash("Enter all fields", "danger")
        else:
            results = Alumni_blog_user.query.filter_by(username=username).first()
            if results:
                result = results.password
                if sha256_crypt.verify(password, result):
                    # passed
                    session["logged_in"] = True
                    session["username"] = username
                    session["password"] = password
                    flash("You are now logged in.", "success")
                    return redirect(url_for("alumni_dashboard"))
                elif not sha256_crypt.verify(password, result):
                    flash("Invalid Password", "danger")
                    return render_template('alumni/alumniblog_login.htm')
            else:
                error = "This username does not exist"
                return render_template("alumni/alumniblog_login.htm", error=error)
    return render_template("alumni/alumniblog_login.htm")


# the alumni blog dashboard
@app.route('/alumni_dashboard', methods=["POST", "GET"])
@logged_ins
def alumni_dashboard():
    results = db.engine.execute("SELECT * FROM alumni_article")
    arts = Alumni_article.query.order_by(Alumni_article.date_created.desc()).all()
    if results:
        return render_template("alumni/alumni_dashboard.htm", arts=arts)
    else:
        msg = "No articles found"
        return render_template("alumni/alumni_dashboard.htm", msg=msg)


# the the alumni blogs page
@app.route("/blogs", methods=["POST", "GET"])
@logged_in
def blogs():
    results = db.engine.execute("SELECT * FROM alumni_article")
    articles = Alumni_article.query.order_by(Alumni_article.date_created.desc()).all()

    if results:
        # image_names = os.listdir('./static/blog_img')
        tags = A_tag.query.all()
        return render_template("alumni/articles.htm", articles=articles, tags=tags)
    else:
        msg = "No articles found"
        return render_template("alumni/articles.htm", msg=msg)


# the alumni search bar
@app.route("/a_search")
@logged_in
def a_search():
    keyword = request.args.get('keyword')
    articles = Alumni_article.query.msearch(
        keyword, fields=['title', 'author', 'category'], limit=20).all()
    tags = A_tag.query.all()

    return render_template("alumni/articles.htm", articles=articles, tags=tags, keyword=keyword)


# the tag for the alumni page 
@app.route("/a_tag/<string:name>", methods=["POST", "GET"])
@logged_in
def a_tag(name):
    # results = db.engine.execute('SELECT article_id FROM tags WHERE tag_id = %s',[id])

    articles = Alumni_article.query.filter_by(category=name).all()

    return render_template("alumni/article_tag.htm", articles=articles)


# the article for the alumni page
@app.route("/blog/<string:id>/", methods=["POST", "GET"])
@logged_in
def blog(id):
    article = Alumni_article.query.filter_by(id=id).first()
    articles = Alumni_article.query.order_by(Alumni_article.date_created.desc()).all()
    comments = Alumni_comment.query.filter_by(alumni_article_id=id).all()
    tags = A_tag.query.all()
    article.views += 1
    db.session.commit()

    if request.method == "POST":
        author = request.form["author"]
        email = request.form["email"]
        message = request.form['message']
        comment = Alumni_comment(author, email, message, id)
        db.session.add(comment)
        article.comments += 1
        flash("Your comment has been submited", "success")
        db.session.commit()
        return redirect(request.url)

    return render_template("alumni/article.htm", comments=comments, article=article, articles=articles, tags=tags)


# the add article for the alumni page 
@app.route("/add_blog", methods=["POST", "GET"])
@logged_ins
def add_blog():
    if request.method == "POST":
        photo = save_image(request.files["photo"])
        # photo = request.files["photo"]
        title = request.form["title"]
        author = request.form['author']
        body = request.form["body"]
        category = request.form["tags"]
        if not body or not title or not photo or not category or not author:
            flash("Enter all fields", "danger")
        else:
            art = Alumni_article(
                photo, title, author, body, category)
            tag = request.form["tags"]
            present_tag = A_tag.query.filter_by(name=tag).first()
            if(present_tag):
                present_tag.blogs_associated.append(art)
            else:
                new_tag = A_tag(name=tag)
                new_tag.blogs_associated.append(art)
                db.session.add(new_tag)

            db.session.add(art)
            db.session.commit()
            flash("Article Created", "success")
            return redirect(url_for("alumni_dashboard"))

    return render_template("alumni/add_blog.htm")


# the url that's send the alumni image
@app.route("/add_blog/<filename>")
@logged_ins
def a_send_image(filename):
    return send_from_directory("./static/a_blog_img", filename)


# the edit alumni article function
@app.route("/edit_blog/<string:id>", methods=["POST", "GET"])
@logged_ins
def edit_blog(id):
    article = Alumni_article.query.filter_by(id=id).first()
    # populate the data
    article_title = article.title
    article_body = article.body
    article_image = article.image
    article_author = article.author
    article_category = article.category
    if request.method == "POST":
        title = request.form["title"]
        author = request.form['author']
        body = request.form["body"]
        category = request.form["tags"]
        if not body or not title or not author or not category:
            flash("Enter all fields", "danger")
        else:
            article = Alumni_article.query.filter_by(id=id).first()
            article.title = title
            article.author = author
            article.body = body
            article.category = category
            # db.engine.execute(
            #     'UPDATE alumni_article SET image=photo,title=title,author=author,body=body,category=category WHERE id =%s',[id]
            # )
            db.session.commit()
            flash("Article Updated", "success")
            return redirect(url_for("alumni_dashboard"))

    return render_template("alumni/edit_blog.htm", article_title=article_title, article_body=article_body,
        article_category=article_category, article_image=article_image, article_author=article_author)


# the alumni delete article session
@app.route("/a_delete_article/<string:id>", methods=["POST"])
@logged_ins
def a_delete_article(id):
    article = Alumni_article.query.filter_by(id=id).first()
    db.session.delete(article)
    db.session.commit()
    flash("Article Deleted", "success")
    return redirect(url_for("alumni_dashboard"))


# the alumni forum page
@app.route('/alumni_forum', methods=["POST", "GET"])
@logged_in
def alumni_forum():
    if request.method == "POST":
        name = request.form["username"]
        email = request.form["email"]
        message = request.form['message']
        forum = Forum(name, email, message)
        db.session.add(forum)
        db.session.commit()
        return redirect(request.url)

    results = db.engine.execute("SELECT * FROM forum")
    forums = Forum.query.order_by(Forum.pub_date.desc()).all()
    if results:

        return render_template("alumni/alumni_forum.htm", forums=forums)
    else:
        msg = "No messages found"
        return render_template("alumni/alumni_forum.htm", msg=msg)

    return render_template("alumni/alumni_forum.htm")


@app.route("/alumni_logout", methods=["POST", "GET"])
@logged_in
def alumni_logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('alumni_login'))


@app.route("/logout", methods=["POST", "GET"])
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.htm'), 404


@app.errorhandler(403)
def page_not_found(e):
    # note that we set the 403 status explicitly
    return render_template('403.htm'), 403


@app.errorhandler(410)
def page_not_found(e):
    # note that we set the 410 status explicitly
    return render_template('410.htm'), 410


@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return render_template('500.htm'), 500


if __name__ == "__main__":
    app.debug = True
    app.run()
