#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, Response, 
  flash, redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
from flask_migrate import Migrate
import sys
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(str(value))
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  venue_areas = Venue.query.distinct(Venue.city, Venue.state)

  for area in venue_areas:
    venues_data = []
    venues = Venue.query.filter_by(city = area.city).filter_by(state = area.state).all()
    for venue in venues:
      venues_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
      })

    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venues_data
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  search_venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  data = []

  for venue in search_venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
    })
  response = {
    "count": len(search_venues),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if not venue:
    return render_template('error/404.html')
  shows = venue.shows
  upcoming_shows = []
  past_shows = []

  for show in shows:
    show.artist_name = show.artist.name
    show.artist_image_link = show.artist.image_link
    if show.start_time > datetime.now():
      upcoming_shows.append(show)
    else:
      past_shows.append(show)

  venue.upcoming_shows = upcoming_shows
  venue.upcoming_shows_count = len(upcoming_shows)
  venue.past_shows = past_shows
  venue.past_shows_count = len(past_shows)

  return render_template('pages/show_venue.html', venue=venue)

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
    venue = Venue(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      address = request.form.get('address'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_talent = True if request.form.get('seeking_talent') == 'Yes' else False,
      seeking_description = request.form.get('seeking_description')
    )

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be added.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully added!')
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists = Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  search_artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  data = []
  num_upcoming_shows = 0
  for artist in search_artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(Show.query.filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all())
    })
  
  response={
    "count": len(search_artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if not artist:
    return render_template('error/404.html')
  
  shows = artist.shows
  upcoming_shows = []
  past_shows = []

  for show in shows:
    show.venue_name = show.venue.name
    show.venue_image_link = show.venue.image_link
    if show.start_time > datetime.now():
      upcoming_shows.append(show)
    else:
      past_shows.append(show)
 
  artist.upcoming_shows = upcoming_shows
  artist.upcoming_shows_count = len(upcoming_shows)
  artist.past_shows = past_shows
  artist.past_shows_count = len(past_shows)
  return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False

  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('webstie')
    artist.seeking_venue = True if request.form.get('seeking_venue')=='Yes' else False
    artist.seeking_description = request.form.get('seeking_description')

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be updated.')
  else:
    flash('Artist was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False

  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('webstie')
    venue.seeking_talent = True if request.form.get('seeking_venue')=='Yes' else False
    venue.seeking_description = request.form.get('seeking_description')

    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be updated.')
  else:
    flash('Venue was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False

  try:
    artist = Artist(
      name = request.form.get('name'),
      city = request.form.get('city'),
      state = request.form.get('state'),
      phone = request.form.get('phone'),
      genres = request.form.getlist('genres'),
      image_link = request.form.get('image_link'),
      facebook_link = request.form.get('facebook_link'),
      website = request.form.get('website'),
      seeking_venue = True if request.form.get('seeking_venue')=='Yes' else False,
      seeking_description = request.form.get('seeking_description')
    )

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be added.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully added!')

  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  for show in shows:
    show.venue_name = show.venue.name
    show.artist_name = show.artist.name
    show.artist_image_link = show.artist.image_link
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show(
      artist_id = request.form.get('artist_id'),
      venue_id = request.form.get('venue_id'),
      start_time = request.form.get('start_time')
    )
    print(show)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully added!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be added.')
  finally:
    db.session.close()

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
