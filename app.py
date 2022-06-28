# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from create_data import movie
from schemas import movie_schema, movies_schema
from models import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')

@movie_ns.route("/")
class MoviesView(Resource):

    def get(self):
        movie_with_genre_and_director = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
                                      Genre.name.label('genre'),
                                      Director.name.label('director')).join(Genre).join(Director)

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.director_id == director_id)
        if genre_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.genre_id == genre_id)

        movies_list = movie_with_genre_and_director.all()

        return movies_schema.dump(movies_list), 200

    def post(self):
        reg_json = request.json
        new_movie = Movie(**reg_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый объект с id {new_movie.id} создан!", 201


@movie_ns.route("/<int:movie_id>")
class MovieView(Resource):

    def get(self, movie_id: int):
        movie = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating, Movie.trailer,
                                 Genre.name.label('genre'),
                                 Director.name.label('director')).join(Genre).join(Director).filter(
            Movie.id == movie_id).first()
        if movie:
            return movie_schema.dump(movie)
        return "Нет такого фильма", 404

    def patch(self, movie_id: int):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404

        reg_json = request.json
        if 'title' in reg_json:
            movie.title = reg_json['title']
        elif 'description' in reg_json:
            movie.description = reg_json['description']
        elif 'trailer' in reg_json:
            movie.trailer = reg_json['trailer']
        elif 'year' in reg_json:
            movie.year = reg_json['year']
        elif 'rating' in reg_json:
            movie.rating = reg_json['rating']
        elif 'genre_id' in reg_json:
            movie.genre_id = reg_json['genre_id']
        elif 'director_id' in reg_json:
            movie.director_id = reg_json['director_id']
        db.session.add(movie)
        db.session.commit
        return f"Объект с id {movie.id} обновлен!", 204

    def put(self, movie_id):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404
        reg_json = request.json

        movie.title = reg_json['title']
        movie.description = reg_json['description']
        movie.trailer = reg_json['trailer']
        movie.year = reg_json['year']
        movie.rating = reg_json['rating']
        movie.genre_id = reg_json['genre_id']
        movie.director_id = reg_json['director_id']
        return f"Объект с id {movie.id} обновлен!", 204

    def delete(self, movie_id):
        movie = db.session.query(Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404
        db.session.delete(movie)
        db.session.commit()
        return f"Объект с id {movie.id} удален!", 204


if __name__ == '__main__':
    app.run(debug=True)
