from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import json

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'cursos.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)

class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    img = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "img": self.img
        }

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    course_reference = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sequence": self.sequence,
            "course_reference": self.course_reference
        }


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_content = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    topic_reference = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "type_content": self.type_content,
            "content": self.content,
            "topic_reference": self.topic_reference,
            "sequence": self.sequence
        }


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    topic_reference = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "options": self.options,
            "topic_reference": self.topic_reference,
        }


@app.route('/get-courses', methods=['GET'])
def get_cursos():
    cursos = Courses.query.order_by(Courses.id).all()
    cursos_json = [curso.to_dict() for curso in cursos]
    return jsonify(cursos_json)

@app.route('/get-topics/<int:course_id>', methods=['GET'])
def get_topics(course_id):
    topics = Topic.query.filter_by(course_reference=course_id).order_by(Topic.sequence).all()
    topics_json = [topic.to_dict() for topic in topics]
    return jsonify(topics_json)

@app.route('/get-content/<int:topic_id>', methods=['GET'])
def get_content(topic_id):
    contents = Content.query.filter_by(topic_reference=topic_id).order_by(Content.sequence).all()
    contents_json = [content.to_dict() for content in contents]
    return jsonify(contents_json)

@app.route('/get-activity/<int:topic_id>', methods=['GET'])
def get_activity(topic_id):
    activity = Activity.query.filter_by(topic_reference=topic_id).first()
    if activity:
        return jsonify(activity.to_dict())
    return jsonify({})

if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists('cursos.db'):
            db.create_all()

        # Carrega dados do JSON
        if os.path.exists("data.json"):
            with open("data.json", "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

            # Insere dados dos cursos
            for course_data in data["courses"]:
                if not Courses.query.filter_by(name=course_data["name"]).first():
                    new_course = Courses(name=course_data["name"], img=course_data["img"])
                    db.session.add(new_course)
            db.session.commit()

            # Insere dados dos tópicos
            course_map = {course.name: course.id for course in Courses.query.all()}
            for topic_data in data["topics"]:
                course_id = course_map.get(topic_data["course_reference"])
                if course_id and not Topic.query.filter_by(name=topic_data["name"], course_reference=course_id).first():
                    new_topic = Topic(
                        name=topic_data["name"],
                        sequence=topic_data["sequence"],
                        course_reference=course_id
                    )
                    db.session.add(new_topic)
            db.session.commit()

            # Insere dados dos conteúdos
            topic_map = {topic.name: topic.id for topic in Topic.query.all()}
            for content_data in data["contents"]:
                topic_id = topic_map.get(content_data["topic_reference"])
                if topic_id and not Content.query.filter_by(content=content_data["content"], topic_reference=topic_id).first():
                    new_content = Content(
                        type_content=content_data["type_content"],
                        content=content_data["content"],
                        topic_reference=topic_id,
                        sequence=content_data["sequence"]
                    )
                    db.session.add(new_content)
            db.session.commit()
        else:
            print('n')

    app.run(debug=True)
