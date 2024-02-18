import pytest

from flask import render_template_string

from udata.core.dataset.factories import DatasetFactory


def render_hook(dataset):
    return render_template_string(
        '{{ hook("dataset.display.transport-banner") }}',
        dataset=dataset
    )


@pytest.fixture
def datasets():
    return DatasetFactory.create_batch(3)


@pytest.mark.frontend
@pytest.mark.usefixtures('clean_db')
@pytest.mark.usefixtures('app')
@pytest.mark.options(THEME='gouvfr')
class TestViews:

    def test_view_dataset_no_extras(self):
        assert '' == render_hook(dataset=DatasetFactory(extras={}))

    def test_view_dataset_with_transport_url(self):
        dataset = DatasetFactory(extras={
            'transport:url': 'http://local.test'
        })

        content = render_hook(dataset=dataset)

        assert dataset.extras['transport:url'] in content
