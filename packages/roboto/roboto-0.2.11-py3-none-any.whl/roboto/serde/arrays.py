def safe_access_array(array, index):
    if array is not None and isinstance(array, list) and len(array) > index:
        return array[index]
    return None
