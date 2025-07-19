from flask import Flask , render_template , redirect , request ,session
from module import config_md_maruf , save_to_db , User , Validate_User , Update_password , save_to_admin , Admin , db , save_to_comment , Comment , Reply , save_to_reply_db , get_votes , Vote
from time_utils import timeago
import re
import os

app = Flask(__name__)
app.secret_key='mdmaruf223'
config_md_maruf(app)

@app.route('/')
def dashboard():
    category = request.args.get('category')
    
    if category:
        all_content_here = Admin.query.filter_by(category=category).order_by(Admin.id.desc()).all()
    else:
        all_content_here = Admin.query.order_by(Admin.id.desc()).all()

    all_comment_here = Comment.query.order_by(Comment.id.desc()).all()
    all_reply_here = Reply.query.order_by(Reply.id.desc()).all()

    for post in all_content_here:
        post.post_time = timeago(post.created_at)
        post.likes, post.dislikes = get_votes(post.id)

    for comment in all_comment_here:
        comment.post_time = timeago(comment.created_at)

    for reply in all_reply_here:
        reply.post_time = timeago(reply.created_at)

    return render_template(
        'dashboard.html',
        all_content_here=all_content_here,
        all_post_here=all_content_here,
        all_comment_here=all_comment_here,
        all_reply_here=all_reply_here
    )

@app.route('/admin_access', methods=['GET', 'POST'])
def admin_access():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '1111':
            session['is_admin'] = True
            return redirect('/admin')
        else:
            return redirect('/')
    return render_template('password.html')

    

@app.route('/register', methods =['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            return render_template('register.html', error="Please enter a valid email.")
        if not re.match(r'^(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$', password):
            return render_template('register.html', error=" Password me kam se kam 1 letter, 1 number aur 1 symbol (@$!%*?&) hona chahiye.")

        if save_to_db(name,email,password):
            return redirect('/login')
        else:
            return render_template('register.html', error = " Email Already Registerd ... ! ")
    return render_template('register.html')

@app.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = Validate_User(email,password)
        if user:
            session['name'] = user.name
            session['email'] = user.email
            return redirect('/')
        else:
            return render_template('login.html', error = " Invalide Email or Password ... ! ")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')



@app.route('/admin')
def admin():
    category = request.args.get('category')
    if category:
        all_post_here = Admin.query.filter_by(category=category).order_by(Admin.id.desc()).all()
    else:
        all_post_here = Admin.query.order_by(Admin.id.desc()).all()
    

    for post in all_post_here:
        post.post_time = timeago(post.created_at)


    return render_template('admin.html', all_post_here=all_post_here)






@app.route('/submit', methods=['POST'])
def submit():
    category = request.form['category']
    heading = request.form['heading']
    descreptions = request.form['descreptions']

    photo = request.files['photo']
    size = len(photo.read())
    photo.seek(0)
    if size > 51200:
        return render_template('admin.html', error =" 50kb se jada photo ki size nhi hoga ...! ")




    file_path = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    photo.save(file_path)
    photo_url = '/'+file_path

    save_to_admin(category, heading , descreptions , photo_url)
    return redirect('/')

@app.route('/delete/<int:user_id>')
def delete(user_id):
    user = Admin.query.get_or_404(user_id)
    file_path = user.photo.lstrip('/')
    if os.path.exists(file_path):
        os.remove(file_path)
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

@app.route('/comment/<int:photo_id>', methods=['POST'])
def comment(photo_id):
    if 'email' not in session:
        return redirect('/login')
    comment_text = request.form['comment']
    save_to_comment(comment_text,photo_id , session['email'], session['name'])
    return redirect('/')

@app.route('/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if 'email' in session and comment.user_email == session['email']:
        db.session.delete(comment)
        db.session.commit()
    return redirect('/')




@app.route('/reply/<int:comment_id>', methods=['POST'])
def reply(comment_id):
    if 'email' not in session:
        return redirect('/login')
    reply_text = request.form['reply']
    save_to_reply_db(reply_text,comment_id , session['email'], session['name'])
    return redirect('/')

@app.route('/delete_reply/<int:reply_id>')
def delete_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    if 'email' in session and reply.user_email == session['email']:
        db.session.delete(reply)
        db.session.commit()
    return redirect('/')

@app.route('/vote/<int:photo_id>/<string:vote_type>')
def vote(photo_id, vote_type):
    if 'email' not in session:
        return redirect('/login')  # ✅ Only logged in user can vote

    user_email = session['email']
    existing_vote = Vote.query.filter_by(user_email=user_email, photo_id=photo_id).first()

    if existing_vote:
        existing_vote.vote_type = vote_type  # Update vote
    else:
        new_vote = Vote(user_email=user_email, photo_id=photo_id, vote_type=vote_type)
        db.session.add(new_vote)

    db.session.commit()
    return redirect('/')





@app.route('/forgot', methods = ['GET','POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user :
            return render_template('reset.html', email=email)
        else:
            return render_template('forgot.html', error = " Email No Found ... ! ")
    return render_template ('forgot.html')
    


@app.route('/reset', methods= ['POST'])
def reset():
    email = request.form['email']
    new_password = request.form['new_password']
    if Update_password (email,new_password):
        return redirect('/login')
    else:
        return " Something Want Wroung ... ! "
    

if __name__ == '__main__':
    app.run(debug=True)

