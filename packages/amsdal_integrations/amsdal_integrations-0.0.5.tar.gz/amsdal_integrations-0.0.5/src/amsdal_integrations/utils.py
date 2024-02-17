def build_address_string(class_name: str, object_id: str, class_version: str = 'LATEST') -> str:
    return f'default#{class_name}:{class_version}:{object_id}:LATEST'
