def class_str_serializer(obj):
    """
    Custom JSON serializer for objects not serializable by default json code.
    """
    return obj.__str__()
