#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import join
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy.orm import load_only
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql
from sqlalchemy import func
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from datetime import datetime
from datetime import date
import time


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

migrate = Migrate(app,db)

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


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  data = []
  lines = []
  
  query_01 = Venue.query.all()
  for row in query_01:
      city = row.city
      state = row.state
      #skip the loop to append City + State if already processed  
      if row.city+row.state in lines:
        continue
      
      #append city + state to lines[] as a identifier to skip it in the next loop  
      lines.append(row.city+row.state)

      query_02 = Venue.query.filter_by(city=city,state=state).all()

      venues = []

      #appending all venues related to the City and State 
      for i in query_02:
        bloco = {
          'id' : i.id,
          'name' : i.name
        }
        venues.append(bloco)

      #creating the branch with the City / State +  all venues related captured in previoous loop
      for i in query_02:
        bloco = {
          'city' : i.city,
          'state' : i.state,
          'venues' : venues
        }

      data.append(bloco)
  print(data)
  
  return render_template('pages/venues.html', areas=data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():

  query = request.form.get('search_term')
  venues = Venue.query.filter(func.lower(Venue.name).contains(query)).with_entities(Venue.id, Venue.name).all()
  data=[]
  for i in venues:
    data.append ({
      'id' : i.id,
      'name': i.name,
      'num_upcoming_shows': 0
    })
    response = {
      'count': len(venues),
      'data': data
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()

  #past_shows = Show.query.filter_by(venue_id=venue_id).filter(Show.start_time < datetime.today()).all()
  #past_shows = Show.query.filter_by(venue_id=venue_id)
  data =[]
  data_upcoming =[]
  past_shows = Show.query.with_entities(Show.artist_id, Show.venue_id, Show.start_time, Venue.name, Artist.name, Artist.image_link).filter(Show.start_time < datetime.today()).join(Artist).join(Venue).filter_by(id=venue_id).all()
  upcoming_shows = Show.query.with_entities(Show.artist_id, Show.venue_id, Show.start_time, Venue.name, Artist.name, Artist.image_link).filter(Show.start_time > datetime.today()).join(Artist).join(Venue).filter_by(id=venue_id).all()
  
 

  for i in past_shows:
   
    data.append({
      'artist_id' : i.artist_id,
      'artist_name' : i[4],
      'artist_image_link': i[5],
      'start_time' : str(i.start_time)
    })

    for i in upcoming_shows:
      data_upcoming.append({
        'artist_id' : i.artist_id,
        'artist_name' : i[4],
        'artist_image_link': i[5],
        'start_time' : str(i.start_time)
      })
      print(data_upcoming)
  

  data = {
    'id' : venue.id,
    'name' : venue.name,
    'genres': str(venue.genres_list)[1:-1].split(','),
    'city' : venue.city,
    'state': venue.state,
    'phone': venue.phone,
    'website': venue.website_link,
    'facebook_link': venue.facebook_link,
    'seeking_talent': venue.seeking_talent,
    'seeking_description': venue.seeking_description,
    'image_link': venue.image_link,
    'past_shows' : data,
    'upcoming_shows': data_upcoming,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows),
    }
  

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  error = False

  try:
    form = VenueForm()
    createvenue = Venue(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    address = form.address.data,
    phone = form.phone.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website_link = form.website_link.data,
    seeking_talent = form.seeking_talent.data,
    genres_list = str(form.genres.data),
    seeking_description = form.seeking_description.data)
    db.session.add(createvenue)
    db.session.commit()
    print(form.genres.data)
  except:
    db.session.rollback()
    print(sys.exec_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The venue ' + request.form['name'] + 'could not be listed') 
    return render_template('pages/home.html')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>/delete', methods=['GET', 'POST'])
def delete_venue(venue_id):

  venue = Venue.query.filter_by(id=venue_id).first()
  name = venue.name
  error = False
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exec_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The venue ' + name + 'could not be deleted') 
    return render_template('pages/venues.html')
  else:
    flash('The venue ' + name + 'was successfully listed') 
    return render_template('pages/venues.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  query = request.form.get('search_term')
  artists = Artist.query.filter(func.lower(Artist.name).contains(query)).with_entities(Artist.id, Artist.name).all()
  data=[]
  for i in artists:
    data.append ({
      'id' : i.id,
      'name': i.name
    })
    response = {
      'count': len(artists),
      'data': data
    }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  past_shows = Show.query.with_entities(Show.venue_id, Show.start_time, Venue.name, Venue.image_link).filter(Show.start_time < datetime.today()).join(Artist).filter_by(id=artist_id).join(Venue).all()
  upcoming_shows = Show.query.with_entities(Show.venue_id, Show.start_time, Venue.name, Venue.image_link).filter(Show.start_time > datetime.today()).join(Artist).filter_by(id=artist_id).join(Venue).all()

  data_past_shows =[]
  data_upcoming_shows= []

  for i in past_shows:
    data_past_shows.append({
      'venue_id': i.venue_id,
      'venue_name' : i[2],
      'venue_image_link': i[3],
      'start_time': str(i.start_time)
    })

  for i in upcoming_shows:
    data_upcoming_shows.append({
      'venue_id': i.venue_id,
      'venue_name' : i[2],
      'venue_image_link': i[3],
      'start_time': str(i.start_time)
    })
 

  artist = Artist.query.filter_by(id=artist_id).first()
  data = {
      'id' : artist.id,
      'name' : artist.name,
      'city' : artist.city,
      'genres': str(artist.genres_list)[1:-1].split(','),
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website_link,
      'facebook_link': artist.facebook_link,
      'seeking_venue': artist.looking_venue,
      'seeking_description': artist.seeking_desc,
      'image_link': artist.image_link,
      'past_shows' : data_past_shows,
      'upcoming_shows': data_upcoming_shows,
      'past_shows_count': len(past_shows),
      'upcoming_shows_count': len(upcoming_shows),
    }

  #print (data)
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  query_artist = Artist.query.filter_by(id=artist_id).first()
  form.name.data = query_artist.name
  form.genres.data= query_artist.genres_list
  form.city.data = query_artist.city
  form.state.data =  query_artist.state
  form.phone.data =  query_artist.phone
  form.website_link.data = query_artist.website_link
  form.facebook_link.data = query_artist.facebook_link
  form.seeking_venue.data = query_artist.looking_venue
  form.seeking_description.data = query_artist.seeking_desc
  form.image_link.data = query_artist.image_link
  
  return render_template('forms/edit_artist.html', form=form, artist=query_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm()
  error = False
  try:
    artist.name = form.name.data
    artist.genres_list = str(form.genres.data)
    artist.city = form.city.data
    artist.state =  form.state.data
    artist.phone = form.phone.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.looking_venue = form.seeking_venue.data
    artist.seeking_desc = form.seeking_description.data
    artist.image_link = form.image_link.data
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exec_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The artist ' + request.form['name'] + 'could not be updated') 
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    flash('Artist ' + request.form['name'] + ' was successfully Updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  query_01 = Venue.query.filter_by(id=venue_id).first()
  
  form.name.data = query_01.name
  form.genres.data= query_01.genres_list
  form.address.data = query_01.address
  form.city.data = query_01.city
  form.state.data =  query_01.state
  form.phone.data =  query_01.phone
  form.website_link.data = query_01.website_link
  form.facebook_link.data = query_01.facebook_link
  form.seeking_talent.data = query_01.seeking_talent
  form.seeking_description.data = query_01.seeking_description
  form.image_link.data = query_01.image_link
    
  return render_template('forms/edit_venue.html', form=form, venue=query_01)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  error = False
  try:
    venue.name = form.name.data
    venue.genres_list = str(form.genres.data)
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state =  form.state.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exec_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The venue ' + request.form['name'] + 'could not be updated') 
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash('Venue ' + request.form['name'] + ' was successfully Updated!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
 
  error = False
  try:
    form = ArtistForm()
    createartist= Artist(
    name = form.name.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    image_link = form.image_link.data,
    facebook_link = form.facebook_link.data,
    website_link = form.website_link.data,
    looking_venue = form.seeking_venue.data,
    genres_list = str(form.genres.data),
    seeking_desc = form.seeking_description.data)
    db.session.add(createartist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exec_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The artist ' + request.form['name'] + 'could not be listed') 
    return render_template('pages/home.html')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []

  #query_join = Show.query.join(Artist, Show.artist_id == Artist.id).join(Venue, Show.venue_id==Venue.id)
  query_join = db.session.query(Show.artist_id, Show.venue_id, Show.start_time, Venue.name, Artist.name, Artist.image_link).join(Artist).join(Venue)
  
  print(query_join)
  
  for i in query_join:
    show = {}
    show["venue_id"] = i[1]
    show["venue_name"] = i[3]
    show["artist_id"] = i[0]
    show["artist_name"] = i[4]
    show["artist_image_link"] = i[5]
    show["start_time"] = str(i[2])
    data.append(show)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False

  try:
    form = ShowForm()
    createshow = Show(
    venue_id = form.venue_id.data,
    artist_id = form.artist_id.data,
    start_time = form.start_time.data)
    db.session.add(createshow)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exec_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. The show could not be listed') 
    return render_template('pages/home.html')
  else:
    flash('Show was successfully listed!')
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
