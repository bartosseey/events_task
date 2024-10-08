import logging
from datetime import datetime, timezone
from flask import Blueprint, jsonify
from flask.views import MethodView
from marshmallow import Schema, fields
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload

from backend.events.ma_schemas import (ParticipantSchema, EventParticipantsSchema, EventSchema,
                                       MealsOnEventSchema, ParticipantMealsOnEventSchema,
                                       ParticipantListOfMealsOnEventSchema)
from backend.events.models import Event, Participant, EventParticipant, MealsOnEvent, ParticipantMealsOnEvent
from backend.extensions import db
from backend.util.db import commit_section
from backend.util.ma_validation import validate_request


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EventSerializationSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    date = fields.DateTime()
    location = fields.String()
    duration = fields.Integer()


class ParticipantSerializationSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    is_vegetarian = fields.Boolean()


class EventParticipantSerializationSchema(Schema):
    id = fields.Integer()
    event_id = fields.Integer()
    days_in_event = fields.Integer()
    participant = fields.Nested(ParticipantSerializationSchema)
    is_event_organizer = fields.Boolean()


class EventsView(MethodView):
    @jwt_required()
    def get(self):
        current_time = datetime.now(timezone.utc)
        logger.debug("Fetching events after current time: %s", current_time)

        events = Event.query.filter(
            Event.date >= current_time.strftime('%Y-%m-%d')
        ).order_by(Event.date).all()

        logger.debug("Fetched events: %s", events)

        event_schema = EventSerializationSchema(many=True)
        events_data = event_schema.dump(events)
        return jsonify(events_data), 200

    @jwt_required()
    @validate_request(EventSchema())
    def post(self, param):
        logger.debug("Creating new event with params: %s", param)
        with commit_section():
            new_event = Event(**param)
            db.session.add(new_event)

        logger.info("Event created successfully: %s", new_event)

        return jsonify({
            "message": "Event created successfully",
            "event": EventSerializationSchema().dump(new_event)
        }), 201


class EventView(MethodView):
    @jwt_required()
    def get(self, event_id):
        logger.debug("Fetching event: %s", event_id)
        event = Event.query.get_or_404(event_id)
        logger.info("Event fetched successfully: %s", event)
        event_schema = EventSerializationSchema()
        event_data = event_schema.dump(event)
        return jsonify(event_data), 200

    @jwt_required()
    @validate_request(EventSchema())
    def patch(self, event_id, param):
        logger.debug("Updating event %s with params: %s", event_id, param)
        event = Event.query.get_or_404(event_id)

        for key, value in param.items():
            setattr(event, key, value)

        with commit_section():
            db.session.add(event)

        logger.info("Event updated successfully: %s", event)

        return jsonify({
            "message": "Event updated successfully",
            "event": EventSerializationSchema().dump(event)
        }), 200

    @jwt_required()
    def delete(self, event_id):
        logger.debug("Deleting event %s", event_id)
        event = Event.query.get_or_404(event_id)

        with commit_section():
            db.session.delete(event)

        logger.info("Event deleted successfully: %s", event_id)

        return jsonify({"message": "Event deleted successfully"}), 204


class ParticipantsView(MethodView):
    @jwt_required()
    def get(self):
        participants = Participant.query.all()
        participant_schema = ParticipantSerializationSchema(many=True)
        participants_data = participant_schema.dump(participants)
        return jsonify(participants_data), 200

    @jwt_required()
    @validate_request(ParticipantSchema())
    def post(self, param):
        logger.debug("Adding new participant")
        with commit_section():
            new_participant = Participant(**param)
            db.session.add(new_participant)
        logger.info("Participant created successfully %s", new_participant)
        return jsonify({
            "message": "Participant created successfully",
            "participant": ParticipantSerializationSchema().dump(new_participant)
         }), 201


class ParticipantView(MethodView):
    @jwt_required()
    def get(self, participant_id):
        participant = Participant.query.get_or_404(participant_id)
        participant_schema = ParticipantSerializationSchema()
        participant_data = participant_schema.dump(participant)
        return jsonify(participant_data), 200

    @jwt_required()
    @validate_request(ParticipantSchema())
    def patch(self, participant_id, param):
        logger.debug("Updating participant %s", participant_id)
        participant = Participant.query.get_or_404(participant_id)

        for key, value in param.items():
            setattr(participant, key, value)

        with commit_section():
            db.session.add(participant)
        logger.info("Participant %s updated successfully", participant_id)
        return jsonify({
            "message": "Participant updated successfully",
            "participant": ParticipantSerializationSchema().dump(participant)
        }), 200

    @jwt_required()
    def delete(self, participant_id):
        logger.debug("Deleting participant %s", participant_id)
        participant = Participant.query.get_or_404(participant_id)

        with commit_section():
            db.session.delete(participant)

        logger.info("Participant deleted successfully: %s", participant_id)

        return jsonify({"message": "Participant deleted successfully"}), 204


class EventParticipantsView(MethodView):
    @jwt_required()
    def get(self, event_id):
        event_participants = (
            EventParticipant.query
            .options(joinedload(EventParticipant.participant))
            .filter_by(event_id=event_id)
            .all()
        )

        event_participants_schema = EventParticipantSerializationSchema(many=True)
        event_participants_data = event_participants_schema.dump(event_participants)

        return jsonify(event_participants_data), 200

    @jwt_required()
    @validate_request(EventParticipantsSchema())
    def post(self, event_id, param):
        logger.debug("Creating new event participant in event %s", event_id)
        param['event_id'] = event_id

        with commit_section():
            new_event_participant = EventParticipant(**param)
            db.session.add(new_event_participant)
        logger.info("Event participant created successfully: %s", new_event_participant)
        return jsonify({
            "message": "Event participant created successfully",
            "event_participant": EventParticipantSerializationSchema().dump(new_event_participant)
        }), 201


class EventParticipantView(MethodView):
    @jwt_required()
    def get(self, event_id, event_participant_id):
        event_participant = EventParticipant.query.filter_by(
            event_id=event_id, id=event_participant_id
        ).first_or_404()
        event_participant_schema = EventParticipantSerializationSchema()
        event_participant_data = event_participant_schema.dump(event_participant)
        return jsonify(event_participant_data), 200

    @jwt_required()
    @validate_request(EventParticipantsSchema())
    def patch(self, event_id, event_participant_id, param):
        logger.debug("Updating event participant %s", event_participant_id)
        event_participant = EventParticipant.query.filter_by(
            event_id=event_id, id=event_participant_id
        ).first_or_404()

        for key, value in param.items():
            setattr(event_participant, key, value)

        with commit_section():
            db.session.add(event_participant)
        logger.info("Event participant updated successfully %s", event_participant)
        return jsonify({
            "message": "Event participant updated successfully",
            "event_participant": EventParticipantSerializationSchema().dump(event_participant)
        }), 200

    @jwt_required()
    def delete(self, event_id, event_participant_id):
        logger.debug("Deleting participant %s from event %s", event_participant_id, event_id)
        event_participant = EventParticipant.query.filter_by(
            event_id=event_id, id=event_participant_id
        ).first_or_404()

        with commit_section():
            db.session.delete(event_participant)

        logger.info("Participant in event deleted successfully: %s", event_participant_id)

        return jsonify({"message": "Event participant deleted successfully"}), 204


class ParticipantUpcomingEventsView(MethodView):
    @jwt_required()
    def get(self, participant_id):
        current_time = datetime.now(timezone.utc)

        upcoming_events = (
            db.session.query(Event)
            .join(EventParticipant)
            .filter(
                EventParticipant.participant_id == participant_id,
                Event.date >= current_time.strftime('%Y-%m-%d')
            )
            .order_by(Event.date)
            .all()
        )

        event_schema = EventSerializationSchema(many=True)
        events_data = event_schema.dump(upcoming_events)
        return jsonify(events_data), 200


class MealsOnEventView(MethodView):
    @jwt_required()
    def get(self, event_id):
        meals_on_event = (
            MealsOnEvent.query
            .filter_by(event_id=event_id)
            .all()
        )

        meals_schema = MealsOnEventSchema(many=True)
        meals_data = meals_schema.dump(meals_on_event)
        return jsonify(meals_data), 200

    @jwt_required()
    @validate_request(MealsOnEventSchema())
    def post(self, event_id, param):
        logger.debug("Creating new meal on event %s", event_id)
        param['event_id'] = event_id

        with commit_section():
            new_meal = MealsOnEvent(**param)
            db.session.add(new_meal)
        logger.info("Meal %s added successfully to event %s", new_meal, event_id)
        return jsonify({
            "message": "Meal added to event successfully",
            "meal": MealsOnEventSchema().dump(new_meal)
        }), 201


class MealOnEventDetailView(MethodView):
    @jwt_required()
    def get(self, event_id, meal_id):
        meal_on_event = MealsOnEvent.query.filter_by(
            event_id=event_id, id=meal_id
        ).first_or_404()

        meal_schema = MealsOnEventSchema()
        meal_data = meal_schema.dump(meal_on_event)
        return jsonify(meal_data), 200

    @jwt_required()
    @validate_request(MealsOnEventSchema())
    def patch(self, event_id, meal_id, param):
        logger.debug("Updating meal %s", meal_id)
        meal_on_event = MealsOnEvent.query.filter_by(
            event_id=event_id, id=meal_id
        ).first_or_404()

        for key, value in param.items():
            setattr(meal_on_event, key, value)

        with commit_section():
            db.session.add(meal_on_event)
        logger.info("Meal updated successfully %s", meal_on_event)
        return jsonify({
            "message": "Meal updated successfully",
            "meal": MealsOnEventSchema().dump(meal_on_event)
        }), 200

    @jwt_required()
    def delete(self, event_id, meal_id):
        logger.debug("Deleting meal %s from event %s", meal_id, event_id)
        meal_on_event = MealsOnEvent.query.filter_by(
            event_id=event_id, id=meal_id
        ).first_or_404()

        with commit_section():
            db.session.delete(meal_on_event)

        logger.info("Meal %s in event %s deleted successfully", meal_id, event_id)

        return jsonify({"message": "Meal deleted successfully"}), 204


class ParticipantMealsOnEventView(MethodView):
    @jwt_required()
    def get(self, event_id, participant_id):
        participant_meals = (
            ParticipantMealsOnEvent.query
            .join(MealsOnEvent)
            .filter(
                ParticipantMealsOnEvent.participant_id == participant_id,
                MealsOnEvent.event_id == event_id
            )
            .all()
        )

        participant_meals_schema = ParticipantMealsOnEventSchema(many=True)
        participant_meals_data = participant_meals_schema.dump(participant_meals)
        return jsonify(participant_meals_data), 200

    @validate_request(ParticipantListOfMealsOnEventSchema())
    @jwt_required()
    def post(self, event_id, participant_id, param):
        logger.debug("Adding meals to event participant %s, %s", participant_id, event_id)
        param['participant_id'] = participant_id
        meals_data = param.get('meals', [])

        created_meals = []

        with commit_section():
            for meal_data in meals_data:
                new_participant_meal = ParticipantMealsOnEvent(**meal_data)

                db.session.add(new_participant_meal)
                created_meals.append(new_participant_meal)
        logger.info("Meals created successfully")
        return jsonify({
            "message": "Participant meals added successfully",
            "participant_meals": ParticipantMealsOnEventSchema(many=True).dump(created_meals)
        }), 201


class ParticipantMealOnEventDetailView(MethodView):
    @jwt_required()
    def get(self, event_id, participant_meal_id):
        participant_meal = ParticipantMealsOnEvent.query.filter_by(
            id=participant_meal_id
        ).first_or_404()

        participant_meal_schema = ParticipantMealsOnEventSchema()
        participant_meal_data = participant_meal_schema.dump(participant_meal)
        return jsonify(participant_meal_data), 200

    @jwt_required()
    @validate_request(ParticipantMealsOnEventSchema())
    def patch(self, event_id, participant_meal_id, param):
        logger.debug("Updating meals")
        participant_meal = ParticipantMealsOnEvent.query.filter_by(
            id=participant_meal_id
        ).first_or_404()

        for key, value in param.items():
            setattr(participant_meal, key, value)

        with commit_section():
            db.session.add(participant_meal)
        logger.info("Participant meal updated successfully")
        return jsonify({
            "message": "Participant meal updated successfully",
            "participant_meal": ParticipantMealsOnEventSchema().dump(participant_meal)
        }), 200

    @jwt_required()
    def delete(self, event_id, participant_meal_id):
        logger.debug("Deleting participant meal %s in event %s", participant_meal_id, event_id)
        participant_meal = ParticipantMealsOnEvent.query.filter_by(
            id=participant_meal_id
        ).first_or_404()

        with commit_section():
            db.session.delete(participant_meal)

        logger.info("Participant meal %s in event %s deleted successfully", participant_meal_id, event_id)

        return jsonify({"message": "Participant meal deleted successfully"}), 204


events_bp = Blueprint('events', __name__)

events_bp.add_url_rule('/events', view_func=EventsView.as_view('events_view'))
events_bp.add_url_rule('/participants', view_func=ParticipantsView.as_view('participants_view'))
events_bp.add_url_rule(
    '/events/<int:event_id>/participants', view_func=EventParticipantsView.as_view('event_participants_view')
)
events_bp.add_url_rule('/events/<int:event_id>', view_func=EventView.as_view('event_view'))
events_bp.add_url_rule(
    '/participants/<int:participant_id>',
    view_func=ParticipantView.as_view('participant_view')
)
events_bp.add_url_rule(
    '/events/<int:event_id>/participants/<int:event_participant_id>',
    view_func=EventParticipantView.as_view('event_participant_view')
)
events_bp.add_url_rule(
    '/participants/<int:participant_id>/upcoming-events',
    view_func=ParticipantUpcomingEventsView.as_view('participant_upcoming_events')
)
events_bp.add_url_rule('/events/<int:event_id>/meals',
                       view_func=MealsOnEventView.as_view('meals_on_event_view'))
events_bp.add_url_rule('/events/<int:event_id>/meals/<int:meal_id>',
                       view_func=MealOnEventDetailView.as_view('meal_on_event_detail_view'))
events_bp.add_url_rule('/events/<int:event_id>/participants/<int:participant_id>/meals',
                       view_func=ParticipantMealsOnEventView.as_view('participant_meals_on_event_view'))
events_bp.add_url_rule('/events/<int:event_id>/participants/<int:participant_id>/meals/<int:participant_meal_id>',
                       view_func=ParticipantMealOnEventDetailView.as_view('participant_meal_on_event_detail_view'))
