class tempVariable:
    def __init__(self, value):
        self._value = value
        self._used = False

    def __repr__(self):
        if self._used:
          raise NameError("tempVariable is already used.")
        self._used = True
        return str(self._value)
