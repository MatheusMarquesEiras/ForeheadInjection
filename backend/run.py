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
        return {"id": self.id, "name": self.name, "img": self.img}


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
            "course_reference": self.course_reference,
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
            "sequence": self.sequence,
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
    return jsonify([c.to_dict() for c in cursos])


@app.route('/get-topics/<int:course_id>', methods=['GET'])
def get_topics(course_id):
    topics = Topic.query.filter_by(course_reference=course_id).order_by(Topic.sequence).all()
    return jsonify([t.to_dict() for t in topics])


@app.route('/get-content/<int:topic_id>', methods=['GET'])
def get_content(topic_id):
    contents = Content.query.filter_by(topic_reference=topic_id).order_by(Content.sequence).all()
    return jsonify([c.to_dict() for c in contents])


@app.route('/get-activity/<int:topic_id>', methods=['GET'])
def get_activity(topic_id):
    activity = Activity.query.filter_by(topic_reference=topic_id).first()
    if activity:
        return jsonify(activity.to_dict())
    return jsonify({})


def seed_from_json():
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
    if not os.path.exists(json_path):
        print("data.json não encontrado, seed ignorado.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    counts = {"courses": 0, "topics": 0, "contents": 0, "activities": 0}

    # Courses — identifica por nome
    for course_data in data.get("courses", []):
        if not Courses.query.filter_by(name=course_data["name"]).first():
            db.session.add(Courses(name=course_data["name"], img=course_data["img"]))
            counts["courses"] += 1
    db.session.commit()

    # Topics — identifica por (nome, curso)
    course_map = {c.name: c.id for c in Courses.query.all()}
    for topic_data in data.get("topics", []):
        course_id = course_map.get(topic_data["course_reference"])
        if course_id is None:
            continue
        if not Topic.query.filter_by(name=topic_data["name"], course_reference=course_id).first():
            db.session.add(Topic(
                name=topic_data["name"],
                sequence=topic_data["sequence"],
                course_reference=course_id,
            ))
            counts["topics"] += 1
    db.session.commit()

    # Contents — identifica por (sequence, topic_id), evita comparar texto longo
    topic_map = {t.name: t.id for t in Topic.query.all()}
    for content_data in data.get("contents", []):
        topic_id = topic_map.get(content_data["topic_reference"])
        if topic_id is None:
            continue
        if not Content.query.filter_by(sequence=content_data["sequence"], topic_reference=topic_id).first():
            db.session.add(Content(
                type_content=content_data["type_content"],
                content=content_data["content"],
                topic_reference=topic_id,
                sequence=content_data["sequence"],
            ))
            counts["contents"] += 1
    db.session.commit()

    # Activities — identifica por topic_id (uma atividade por tópico)
    for activity_data in data.get("activities", []):
        topic_id = topic_map.get(activity_data["topic_reference"])
        if topic_id is None:
            continue
        if not Activity.query.filter_by(topic_reference=topic_id).first():
            db.session.add(Activity(
                question=activity_data["question"],
                options=activity_data["options"],
                topic_reference=topic_id,
            ))
            counts["activities"] += 1
    db.session.commit()

    added = {k: v for k, v in counts.items() if v > 0}
    if added:
        print(f"Seed: novos registros adicionados — {added}")
    else:
        print("Seed: nenhum registro novo encontrado.")


# Roda sempre que o app sobe, independente de como for iniciado (python run.py ou WSGI)
with app.app_context():
    db.create_all()
    seed_from_json()

if __name__ == "__main__":
    app.run(debug=True)
