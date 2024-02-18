def get_schema():
    return dict(
        name='Account Updated',
        description='Account Updated based on provided data',
        is_trigger=True,
        schema=dict(
            type='object',
            additionalProperties=False,
            description='Account updated',
            required=['inputs', 'outputs'],
            properties=dict(
                inputs=dict(
                    type='object',
                    additionalProperties=False,
                    required=["is_inherited"],
                    properties=dict(
                        is_inherited=dict(
                            type='boolean',
                            default=False
                        ),
                    )
                ),
                outputs=dict(
                    type='object',
                    required=[
                        'account_uuid'
                        'parent_uuids',
                        'name',
                        'created_ts'
                        'updated_ts'
                    ],
                    properties=dict(
                        account_uuid=dict(
                            type='string',
                        ),
                        account_type_uuid=dict(
                            type='string',
                        ),
                        parent_uuids=dict(
                            type='array',
                            items=dict(
                                type='string',
                                format='uuid'
                            )
                        ),
                        name=dict(
                            type='string'
                        ),
                        created_ts=dict(
                            type='integer',
                        ),
                        updated_ts=dict(
                            type='integer',
                        )
                    )
                ),
            )
        )
    )


def process(workflow_uuid, node_uuid, processed_ts, inputs, integration, **kwargs):
    pass
