def validateField(parent_field_name=None, child_field_name=None):

    if child_field_name == None:
        if parent_field_name == None:
            return 'NOT_FOUND'
    else:
        
        field_value = 'NOT_FOUND'
        if parent_field_name[child_field_name] != None:
            field_value = parent_field_name.get(child_field_name)

        return {
            child_field_name: field_value
        }
