from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<title: {self.title}>'

with app.app_context():
    db.create_all()


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    all_posts = db.session.query(BlogPost).all()  # Query all database
    return render_template("index.html", all_posts=all_posts)


@app.route("/post/<int:index>")
def show_post(index):
    # requested_post = None
    post = db.session.query(BlogPost).get(index)  # Query database by index
    print(post.title)
    # for blog_post in all_posts:
    #     # print(blog_post['id'])
    #     if blog_post["id"] == index:
    #         requested_post = blog_post
    return render_template("post.html", post=post)


@app.route("/new-post", methods=['POST', 'GET'])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        date_post = datetime.today().strftime("%B %d, %Y")
        add_post = BlogPost(title=form.title.data,
                            date=f'{date_post}',
                            body=form.body.data,
                            author=form.author.data,
                            img_url=form.img_url.data,
                            subtitle=form.subtitle.data)
        db.session.add(add_post)
        db.session.commit()
        return redirect("/")
    return render_template("make-post.html", form=form, header='New Post')


@app.route("/edit-post/<int:id>", methods=["POST", "GET"])
def edit_post(id):
    post_to_edit = BlogPost.query.get(id)
    form = CreatePostForm()
    # get data from existing data and send it to wtform to display in html as sample below
    edit_form = CreatePostForm(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        author=post_to_edit.author,
        img_url=post_to_edit.img_url,
        body=post_to_edit.body
    )
    print(post_to_edit.author)
    if edit_form.validate_on_submit():
        # get post that want to edit and enter with new data from wtform
        post_to_edit.title = form.title.data
        post_to_edit.subtitle = form.subtitle.data
        post_to_edit.author = form.author.data
        post_to_edit.img_url = form.img_url.data
        post_to_edit.body = form.body.data
        db.session.commit()
        return redirect("/")
    return render_template("make-post.html", header='Edit Post', form=edit_form)


@app.route("/delete/<int:id>", methods=["POST", "GET"])
def delete(id):
    post_to_delete = BlogPost.query.get(id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

# if __name__ == "__main__":
#     app.run(host='localhost', port=1080)
