from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import func
from sqlalchemy import exc
import re
db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add validators 
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) == 0:
            raise ValueError('Author must have a name')
        # Check for unique name (only if id is None, i.e., new record)
        if self.id is None:
            try:
                existing = db.session.query(Author).filter(func.lower(Author.name) == func.lower(name.strip())).first()
                if existing:
                    raise ValueError('Author name must be unique')
            except exc.OperationalError:
                # If table doesn't exist yet, let the database's unique constraint handle it later
                pass
        return name.strip()

    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if phone_number is not None:
            if not re.match(r'^\d{10}$', phone_number):
                raise ValueError('Phone number must be exactly 10 digits')
        return phone_number

    def __repr__(self):
        return f'Author(id={self.id}, name={self.name})'

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    category = db.Column(db.String)
    summary = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    # Add validators  
    @validates('title')
    def validate_title(self, key, title):
        if not title or len(title.strip()) == 0:
            raise ValueError('Post must have a title')
        # Check for clickbait - title starting with "Why I" (exactly "Why I")
        if re.match(r'^Why I\b', title, re.IGNORECASE):
            raise ValueError('Title must not be clickbait')
        return title

    @validates('content')
    def validate_content(self, key, content):
        if content is not None and len(content) < 250:
            raise ValueError('Content must be at least 250 characters')
        return content

    @validates('summary')
    def validate_summary(self, key, summary):
        if summary is not None and len(summary) > 250:
            raise ValueError('Summary must be at most 250 characters')
        return summary

    @validates('category')
    def validate_category(self, key, category):
        if category not in ['Non-Fiction', 'Fiction']:
            raise ValueError('Category must be Non-Fiction or Fiction')
        return category


    def __repr__(self):
        return f'Post(id={self.id}, title={self.title} content={self.content}, summary={self.summary})'
