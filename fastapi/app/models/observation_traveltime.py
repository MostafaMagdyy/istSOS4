from .database import Base, SCHEMA_NAME
from sqlalchemy.sql.schema import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Integer, Text, Float, Boolean
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql.json import JSON
from sqlalchemy.dialects.postgresql.ranges import TSTZRANGE
from sqlalchemy.dialects.postgresql.base import TIMESTAMP

class ObservationTravelTime(Base):
    __tablename__ = 'Observation_traveltime'

    id = Column(Integer)
    self_link = Column("@iot.selfLink", Text)
    feature_of_interest_navigation_link = Column("FeatureOfInterest@iot.navigationLink", Text)
    datastream_navigation_link = Column("Datastream@iot.navigationLink", Text)
    phenomenon_time = Column("phenomenonTime", TIMESTAMP, nullable=False)
    result_time = Column("resultTime", TIMESTAMP, nullable=False)
    result_string = Column("resultString", Text)
    result_integer = Column("resultInteger", Integer)
    result_double = Column("resultDouble", Float)
    result_boolean = Column("resultBoolean", Boolean)
    result_json = Column("resultJSON", JSON)
    result_quality = Column("resultQuality", JSON)
    valid_time = Column("validTime", TSTZRANGE)
    parameters = Column(JSON)
    datastream_id = Column(Integer, ForeignKey(f'{SCHEMA_NAME}.Datastream.id'), nullable=False)
    featuresofinterest_id = Column(Integer, ForeignKey(f'{SCHEMA_NAME}.FeaturesOfInterest.id'), nullable=False)
    system_time_validity = Column(TSTZRANGE)

    __table_args__ = (PrimaryKeyConstraint(id, system_time_validity), {'schema': SCHEMA_NAME })

    def _serialize_columns(self):
        """Serialize model columns to a dict, applying naming transformations."""
        rename_map = {
            'id': '@iot.id',
            'self_link': '@iot.selfLink',
            'feature_of_interest_navigation_link': 'FeatureOfInterest@iot.navigationLink',
            'datastream_navigation_link': 'Datastream@iot.navigationLink',
            "phenomenon_time": "phenomenonTime",
            "result_time": "resultTime",
            "result_quality": "resultQuality",
            "valid_time": "validTime"
        }
        serialized_data = {
            rename_map.get(attr.key, attr.key): getattr(self, attr.key)
            for attr in self.__class__.__mapper__.column_attrs
            if attr.key not in inspect(self).unloaded
        }
        if 'phenomenon_time' in serialized_data and self.phenomenon_time is not None:
            serialized_data['phenomenonTime'] = self.phenomenon_time.isoformat()
        if 'result_time' in serialized_data and self.result_time is not None:
            serialized_data['resultTime'] = self.result_time.isoformat()
        if 'valid_time' in serialized_data and self.valid_time is not None:
            serialized_data['validTime'] = self._format_datetime_range(self.valid_time)
        if 'system_time_validity' in serialized_data and self.system_time_validity is not None:
            serialized_data['system_time_validity'] = self._format_datetime_range(self.system_time_validity)
        return serialized_data

    def _handle_result_fields(self, data):
        """Handle the serialization of result fields to unify under a single 'result' field."""
        result_fields = ['result_string', 'result_integer', 'result_double', 'result_boolean', 'result_json']
        for field in result_fields:
            if field in data and data[field] is not None:
                data['result'] = data.pop(field, None)
            else:
                data.pop(field, None)

    def to_dict_expand(self):
        """Serialize the ObservationTravelTime model to a dict, excluding 'system_time_validity' and handling result fields."""
        data = self._serialize_columns()
        self._handle_result_fields(data)
        return data

    def _format_datetime_range(self, range_obj):
        if range_obj:
            lower = getattr(range_obj, 'lower', None)
            upper = getattr(range_obj, 'upper', None)
            return f"{lower.isoformat()}/{upper.isoformat()}"

        return None