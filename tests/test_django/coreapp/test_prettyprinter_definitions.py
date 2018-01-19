import pytest
from prettyprinter import install_extras, pformat

from coreapp.models import MyModel

install_extras(['django'])


@pytest.mark.django_db
def test_simple_case():
    instance = MyModel.objects.create(name='John', version=2)
    expected_uuid = "uuid.UUID('{}')".format(str(instance.uuid))
    expected = """\
coreapp.models.MyModel(
    id={},
    uuid={},
    version=2,
    name='John'
)""".format(instance.id, expected_uuid)
    assert pformat(instance, width=999) == expected


@pytest.mark.django_db
def test_blank_field():
    instance = MyModel.objects.create(name='', version=2)
    expected_uuid = "uuid.UUID('{}')".format(str(instance.uuid))
    expected = """\
coreapp.models.MyModel(
    id={},
    uuid={},
    version=2,
    # Blank fields: name
)""".format(instance.id, expected_uuid)
    assert pformat(instance, width=999) == expected


@pytest.mark.django_db
def test_default_field():
    instance = MyModel.objects.create(name='', version=1)
    expected_uuid = "uuid.UUID('{}')".format(str(instance.uuid))
    expected = """\
coreapp.models.MyModel(
    id={},
    uuid={},
    # Blank fields: name
    # Default value fields: version
)""".format(instance.id, expected_uuid)
    assert pformat(instance, width=999) == expected
