from .integration_types import *
from .integrations import *


def get_schema():
    return dict(
        type='object',
        additionalProperties=False,
        description='Integration Service',
        required=['extra_attributes', 'credentials'],
        properties=dict(
            extra_attributes=dict(
                type='object',
                additionalProperties=False,
                properties=dict()
            ),
            credentials=dict(
                type='object',
                additionalProperties=False,
                required=[],
                properties=dict()
            )
        )
    )


def connect(extra_attributes, credentials):
    return dict()
