#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser, datetime
import babel
import sys
from flask import (
  Flask,
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import or_
import logging
from logging import Formatter, FileHandler
#from flask_wtf import Form
from forms import *
from flask_migrate import Migrate 
from models import db, Venue, Artist,Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#db = SQLAlchemy(app)
db = db.init_app(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models. >> Move to model.py
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120),unique = True, nullable = False )
    # name must be unique
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500), nullable = False)
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    show = db.relationship('Show', backref='Venue')

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique = True, nullable = False)
    # name must be unique
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default = False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    show = db.relationship('Show', backref='Artist')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)
    date = db.Column(db.String(120))


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#---------------------------------------------------------------------------#
# Define show finder
#---------------------------------------------------------------------------#

def find_upcoming_shows_for_artist(artist_id):
    upcoming_shows_data =[]
    # Use Join to join Venue to Show
    upcoming_shows1 = db.session.query(Show,Venue).\
      join(Venue).\
      filter(Show.artist_id == artist_id,\
        Show.date > datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      ).all()
    for show in upcoming_shows1: 
    # show is list. example (<Show 1> <Artist 1>)
      data2={
          "venue_id": show.Show.venue_id,
          "venue_name": show.Venue.name,
          "venue_image_link": show.Venue.image_link,
          "start_time": show.Show.date        
        }
      upcoming_shows_data.append(data2)
    return len(upcoming_shows_data), upcoming_shows_data

def find_past_shows_for_artist(artist_id):
  past_shows_data =[]
  # Use Join to join Venue to Show
  past_shows1 = db.session.query(Show,Venue).\
    join(Venue).\
    filter(Show.artist_id == artist_id,\
      Show.date < datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ).all()
  for show in past_shows1: 
  # show is a tapple, example (<Show 1> <Artist 1>)
    data2={
        "venue_id": show.Show.venue_id,
        "venue_name": show.Venue.name,
        "venue_image_link": show.Venue.image_link,
        "start_time": show.Show.date        
      }
    past_shows_data.append(data2)
  return len(past_shows_data), past_shows_data

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # find function upcoming shows of a venue

  # find all cities at first
  cities = set()
  all_cities = Venue.query.all()
  for city in all_cities:
    cities.add(city.city)
  data=[]
  # make venues data for each city.
  for city in cities:
    venues_query = Venue.query.filter_by(city=city).all()
    venues_data = []
    for venue_in_city in venues_query:
      venue_data ={
        'id': venue_in_city.id,
        'name':venue_in_city.name,
        'num_upcoming_shows':  \
          db.session.query(Show).\
          filter(Show.venue_id == venue_in_city.id,\
            Show.date > datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ).count()
      }
      venues_data.append(venue_data)
    data_in_city = {
      'city': city,
      'state': venues_query[0].state,
      'venues': venues_data
    }
    data.append(data_in_city)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term')
  search_results = Venue.query.filter(or_(Venue.name.ilike(f'%{search_term}%'))).all()
  data=[]
  for venue in search_results:
    data1 ={
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": \
        db.session.query(Show).\
        filter(Show.venue_id == venue.id,\
        Show.date > datetime.now().strftime('%Y-%m-%d %H:%M:%S')).count()
    }
    data.append(data1)
  response={
    "count": len(search_results),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  def find_past_shows(venue_id):
    past_shows_data1 =[]    
    past_shows = db.session.query(Show,Artist).join(Artist).\
      filter(Show.venue_id==venue_id, \
        Show.date < datetime.now().strftime('%Y-%m-%d %H:%M:%S')).all()
    for show in past_shows:
      artist = show[1]
      data3={
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show[0].date        
      }
      past_shows_data1.append(data3)

    return past_shows_data1

  def find_upcoming_shows(venue_id):
    upcoming_shows_data1 =[]    
    upcoming_shows = db.session.query(Show,Artist).join(Artist).\
      filter(Show.venue_id==venue_id, \
        Show.date > datetime.now().strftime('%Y-%m-%d %H:%M:%S')).all()
    for show in upcoming_shows:
      artist = show[1]
      data3={
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show[0].date        
      }
      upcoming_shows_data1.append(data3)

    return upcoming_shows_data1
  data =[]
  for venue in Venue.query.all():
    data1={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": find_past_shows(venue.id),
      "upcoming_shows": find_upcoming_shows(venue.id),
      "past_shows_count": \
        db.session.query(Show).\
        filter(Show.venue_id == venue.id,\
        Show.date < datetime.now().strftime('%Y-%m-%d %H:%M:%S')).count(),
      "upcoming_shows_count": \
        db.session.query(Show).\
        filter(Show.venue_id == venue.id,\
        Show.date > datetime.now().strftime('%Y-%m-%d %H:%M:%S')).count(),
      }
    data.append(data1)

  data = list(filter(lambda d: d['id'] == venue_id, data))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    db.session.commit()
    print('!!! Venue Create error !!!!')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + venue_id + ' was successfully deleted!')
  except:
    db.session.rollback()
    db.session.commit()
  finally:
    db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
# TODO: replace with real data returned from querying the database
def artists():
  # make artists data
  data=[]
  for artist  in Artist.query.all():
    data1 ={
      "id": artist.id,
      "name": artist.name}
    data.append(data1)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term')
  search_results = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data=[]
  for artist in search_results:
    num_upcoming_shows, d = find_upcoming_shows_for_artist(artist.id)
    data1 ={
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming_shows,
    }
    data.append(data1)
  response={
    "count": len(search_results),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = []
  for artist in Artist.query.all():
    upcoming_shows_count, upcoming_shows =  find_upcoming_shows_for_artist(artist.id)
    past_shows_count, past_shows = find_past_shows_for_artist(artist.id)
    data1 ={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count,

    }
    data.append(data1)
  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data,
    artist.city = form.city.data,
    artist.state = form.state.data,
    artist.phone = form.phone.data,
    artist.image_link = form.image_link.data,
    artist.website = form.website.data,
    artist.facebook_link =form.facebook_link.data,
    artist.genres = form.genres.data
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    db.session.commit()
    print('!!! Artist Edit error !!!!')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue_data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website = form.website.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link =  form.image_link.data
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    db.session.commit()
    print('!!! Venue Edit error !!!!')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  error = False
  try:
    insert_artist_data = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      image_link = form.image_link.data,
      website = form.website.data,
      facebook_link =form.facebook_link.data,
      genres = form.genres.data
    )
    db.session.add(insert_artist_data)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    db.session.commit()
    print('!!! Artist Create error !!!!')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data =[]
  for show in Show.query.all():
    data1={
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.date
    }
    data.append(data1)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  error = False
  try:
    insert_show_data = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      date = form.start_time.data
    )
    db.session.add(insert_show_data)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    db.session.commit()
    print('!!! Show Create error !!!!')
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
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
