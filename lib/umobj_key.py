def create_directory(key):
    """
        Create a directry (key will always end in a /)
    """
    try:
        key.set_contents_from_string('')
        return True
    except IOError, e:
        print e
        return False
