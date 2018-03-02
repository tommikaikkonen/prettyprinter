import pytest
from prettyprinter import install_extras, pformat

from coreapp.models import MyModel

install_extras(['django'])


@pytest.mark.django_db
def test_simple_case():
    instance = MyModel.objects.create(name='John', slug='john', version=2)
    expected = """\
coreapp.models.MyModel(
    id={},
    slug='john',
    version=2,
    name='John',
    # Default value fields: kind
)""".format(
        instance.id
    )
    assert pformat(instance, width=999) == expected


@pytest.mark.django_db
def test_blank_field():
    instance = MyModel.objects.create(name='', slug=None, version=2)
    expected = """\
coreapp.models.MyModel(
    id={},
    version=2,
    # Null fields: slug
    # Blank fields: name
    # Default value fields: kind
)""".format(instance.id)
    assert pformat(instance, width=999) == expected


@pytest.mark.django_db
def test_default_field():
    instance = MyModel.objects.create(name='', slug='a', version=1)
    expected = """\
coreapp.models.MyModel(
    id={},
    slug='a',
    # Blank fields: name
    # Default value fields: kind, version
)""".format(instance.id)
    assert pformat(instance, width=999) == expected


@pytest.mark.django_db
def test_choices_display():
    instance = MyModel.objects.create(
        name='John',
        slug='john',
        version=1,
        kind='B'
    )
    expected = """\
coreapp.models.MyModel(
    id={},
    slug='john',
    kind='B',  # Display for B
    name='John',
    # Default value fields: version
)""".format(instance.id)
    assert pformat(instance, width=999) == expected

@pytest.mark.django_db
def test_queryset():
    for i in range(11):
        MyModel.objects.create(
            name='Name{}'.format(i),
            version=1,
            slug='slug-{}'.format(i)
        )

    qs = MyModel.objects.all()
    assert pformat(qs, width=999) == """\
django.db.models.query.QuerySet([
    coreapp.models.MyModel(id=1),
    coreapp.models.MyModel(id=2),
    coreapp.models.MyModel(id=3),
    coreapp.models.MyModel(id=4),
    coreapp.models.MyModel(id=5),
    coreapp.models.MyModel(id=6),
    coreapp.models.MyModel(id=7),
    coreapp.models.MyModel(id=8),
    coreapp.models.MyModel(id=9),
    coreapp.models.MyModel(id=10),
    coreapp.models.MyModel(id=11)
])"""
