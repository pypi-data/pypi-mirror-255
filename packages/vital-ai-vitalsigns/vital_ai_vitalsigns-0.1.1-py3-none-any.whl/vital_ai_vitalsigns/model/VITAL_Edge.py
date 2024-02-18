from vital_ai_vitalsigns.impl import VitalSignsImpl
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.model.properties.StringProperty import StringProperty
from vital_ai_vitalsigns.model.trait.PropertyTrait import PropertyTrait


class VITALEdge(GraphObject):
    allowed_properties = [
        {'uri': "http://vital.ai/ontology/vital-core#hasName", 'prop_class': StringProperty},
    ]