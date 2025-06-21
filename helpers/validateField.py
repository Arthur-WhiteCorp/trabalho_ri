def validateField(parent_field_name=None, child_field_name=None):
    if parent_field_name is None or child_field_name is None:
        return 'NOT_FOUND'
    
    field_value = parent_field_name.get(child_field_name)
    if field_value is None:
        return 'NOT_FOUND'
    
    return field_value
