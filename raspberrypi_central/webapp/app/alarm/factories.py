import factory
from faker import Factory

from devices.factories import DeviceFactory
from .models import CameraRectangleROI

faker = Factory.create()

class CameraRectangleROIFactory(factory.DjangoModelFactory):
    class Meta:
        model = CameraRectangleROI

    x = 0
    y = 0
    w = 0
    h = 0

    definition_width = 100
    definition_height = 100

    device = factory.SubFactory(DeviceFactory)