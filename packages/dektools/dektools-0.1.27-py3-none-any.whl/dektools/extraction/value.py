class NotExist:
    def __bool__(self):
        return False


class ProxyValue:
    NOT_EXIST = NotExist()

    def __init__(self, value):
        self.value = value

    def get(self, *keys):
        cursor = self.value
        for key in keys:
            if hasattr(cursor, '__getitem__'):
                try:
                    cursor = cursor[key]
                except (IndexError, TypeError):
                    try:
                        key = int(key)
                        try:
                            cursor = cursor[key]
                        except (IndexError, TypeError):
                            return self.NOT_EXIST
                    except ValueError:
                        return self.NOT_EXIST
            else:
                try:
                    cursor = getattr(cursor, key)
                except AttributeError:
                    return self.NOT_EXIST
        return cursor
