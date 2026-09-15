from flask import Flask, render_template, request, url_for, session, flash, redirect
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = "library123"
members = {}
books = [
    {'title': 'Harry Potter',
     'author': 'J.K.Rowling',
     'category':'Fiction',
     'copies':5},
     {'title':'Atomic Habits',
      'author':'James Clear',
      'category':'Self Help',
      'copies':4
     },
     {'title':'The Alchemist',
      'author': 'Paulo Coelho',
      'category':'Fiction',
      'copies':3
      },
      {'title': 'Rich Dad Poor Dad',
       'author':'Robert Kiyosaki',
       'category':'Finance',
       'copies': 4
       },
     {
        'title': 'The Psychology of Money',
        'author': 'Morgan Housel',
        'category': 'Finance',
        'copies': 3
    } 

]
issued_books = []
# HOME
@app.route('/')
def home():
    return render_template('home.html')

# CATALOG
@app.route('/catalog')
def catalog():
    search = request.args.get('search', '').lower()
    filtered_books = []
    for book in books:
        if search in book['title'].lower() or search in book['author'].lower():
            filtered_books.append(book)
    return render_template('catalog.html', books=filtered_books)


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if username in members:
            flash("Username already exists!")
            return redirect(url_for('register'))
        members[username] = {
            'name': name,
            'email': email,
            'password': password
        }
        flash("Registration successful! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')


# MEMBER LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in members and members[username]['password'] == password:
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('member_dashboard'))
        else:
            flash("Invalid username or password!")
    return render_template('login.html')

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('admin', None)
    flash("Logged out successfully!")
    return redirect(url_for('home'))

# ADMIN LOGIN
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            session['admin'] = True
            flash("Admin login successful!")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin username or password!")
    return render_template('admin_login.html')

# ADMIN DASHBOARD
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash("Please login as admin")
        return redirect(url_for('admin_login'))
    overdue_count = 0
    today = datetime.now()
    for issue in issued_books:
        if today > issue['due_date']:
           overdue_count += 1
    return render_template(
        'admin_dashboard.html',
        total_book=len(books),
        total_members=len(members),
        total_issued=len(issued_books),
        overdue_count=overdue_count
    )


# ADD BOOK
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'admin' not in session:
        flash("Please login as admin")
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        copies = request.form['copies']
        book = {
            'title': title,
            'author': author,
            'category': category,
            'copies': copies
        }
        books.append(book)
        flash("Book added successfully!")
        return redirect(url_for('catalog'))
    return render_template('add_book.html')


# EDIT BOOK
@app.route('/edit-book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'admin' not in session:
        flash("Please login as admin")
        return redirect(url_for('admin_login'))
    if book_id < 0 or book_id >= len(books):
       flash("Book not found!")
       return redirect(url_for('catalog'))
    book = books[book_id]
    if request.method == 'POST':
        book['title'] = request.form['title']
        book['author'] = request.form['author']
        book['category'] = request.form['category']
        book['copies'] = request.form['copies']
        flash("Book updated successfully!")
        return redirect(url_for('catalog'))
    return render_template(
        'edit_book.html',
        book=book,
        book_id=book_id
    )

# DELETE BOOK
@app.route('/delete-book/<int:book_id>')
def delete_book(book_id):
    if 'admin' not in session:
        flash("Please login as admin")
        return redirect(url_for('admin_login'))
    if book_id >= 0 and book_id < len(books):
        books.pop(book_id)
        flash("Book deleted successfully!")
        return redirect(url_for('catalog'))

# ISSUE BOOK
@app.route('/issue-book', methods=['GET', 'POST'])
def issue_book():
    if 'admin' not in session:
        flash("Please login as admin")
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        username = request.form['username']
        book_id = int(request.form['book_id'])
        if int(books[book_id]['copies']) > 0:
            issue_date = datetime.now()
            due_date = issue_date + timedelta(days=14)
            issued_books.append({
                'username': username,
                'book_id': book_id,
                'issue_date': issue_date,
                'due_date': due_date
            })
            books[book_id]['copies'] = int(books[book_id]['copies']) - 1
            flash("Book issued successfully!")
            return redirect(url_for('issued_books_list'))
        else:
            flash("Book is not available!")
    return render_template(
        'issue_book.html',
        members=members,
        books=books
    )

# ISSUED BOOK LIST
@app.route('/issued-books')
def issued_books_list():
    if 'admin' not in session:
        flash("Please login as admin")
        return redirect(url_for('admin_login'))
    return render_template(
        'issued_books.html',
        issued_books=issued_books,
        members=members,
        books=books
    )

# RETURN BOOK
@app.route('/return-book/<int:index>')
def return_book(index):
    if 'admin' not in session:
        flash("Please login as admin")
        return redirect(url_for('admin_login'))
    if index >= 0 and index < len(issued_books):
        issue = issued_books[index]
        today = datetime.now()
        if today > issue['due_date']:
            late_days = (today - issue['due_date']).days
            fine = late_days * 10
        else:
            fine = 0
        book_id = issue['book_id']
        books[book_id]['copies'] = int(books[book_id]['copies']) + 1
        issued_books.pop(index)
        flash(f"Book returned successfully! Fine: Rs. {fine}")
    return redirect(url_for('issued_books_list'))

# MEMBER DASHBOARD
@app.route('/member-dashboard')
def member_dashboard():
    if 'username' not in session:
        flash("Please login first!")
        return redirect(url_for('login'))
    username = session['username']
    member_books = []
    for issue in issued_books:
        if issue['username'] == username:
            today = datetime.now()
            if today > issue['due_date']:
                late_days = (today - issue['due_date']).days
                issue['fine'] = late_days * 10
            else:
                issue['fine']=0
            member_books.append(issue)
    return render_template(
        'member_dashboard.html',
        member_books=member_books,
        books=books
    )


if __name__ == '__main__':
    app.run(debug=True)