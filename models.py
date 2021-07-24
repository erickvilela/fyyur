from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref


db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(400))
    seeking_talent = db.Column(db.Boolean)
    genres_list = db.Column(db.Text)
    seeking_description = db.Column(db.String(500))


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres_list = db.Column(db.Text)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(250))
    looking_venue = db.Column(db.Boolean)
    seeking_desc = db.Column(db.String(500))


class Show(db.Model):
  __tablename__= 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
  parent = relationship(Venue, backref=backref("venue", cascade="all,delete"))
  start_time = db.Column(db.DateTime)
