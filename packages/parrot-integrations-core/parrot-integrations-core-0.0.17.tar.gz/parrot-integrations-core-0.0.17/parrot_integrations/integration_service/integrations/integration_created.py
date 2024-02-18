def get_schema():
    return dict(
        name='',
        description='',
        is_trigger=True,
        schema=dict(
            type='object',
            additionalProperties=False,
            description='',
            required=['inputs', 'outputs'],
            properties=dict(
                inputs=dict(
                    type='object',
                    additionalProperties=False,
                    required=[],
                    properties=dict(
                    )
                ),
                outputs=dict(
                    type='object',
                    additionalProperties=True,
                    required=[],
                    properties=dict()
                ),
            )
        )
    )


def process(workflow_uuid, node_uuid, processed_ts, inputs, integration, **kwargs):
    pass
