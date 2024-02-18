def evaluate_filter(filters, record):
    operations = []
    for operation in filters.get('operations', []):
        if 'operations' in operation.keys():
            result = evaluate_filter(filters=operation, record=record)
        else:
            result = evaluate_criteria(criteria=operation, record=record)
        operations.append(result)
    return evaluate_operations(operations=operations, operator=filters['operator'])


def evaluate_operations(operations, operator):
    if len(operations) == 0:
        result = True
    elif operator == 'and':
        result = all(operations)
    elif operator == 'or':
        result = any(operations)
    else:
        if len(operations) != 1:
            raise SyntaxError("'not' Operator only works on single operation")
        result = not all(operations)
    return result


def evaluate_criteria(criteria, record):
    from .common import extract_value
    result = False
    try:
        left = extract_value(field=criteria['left'], record=record)
        right = extract_value(field=criteria['right'], record=record)
        if criteria['operator'] == '==':
            result = left == right
        elif criteria['operator'] == '!=':
            result = left != right
        elif criteria['operator'] == '>=':
            result = left >= right
        elif criteria['operator'] == '<=':
            result = left <= right
        elif criteria['operator'] == '<':
            result = left < right
        elif criteria['operator'] == '>':
            result = left > right
        elif criteria['operator'] == 'contains':
            result = right in left
    except Exception:
        pass
    finally:
        return result



