from . import _DPType, Array, Boolean, Float, Integer, Null, Object, String


class Any(_DPType):
    """
    `Any` is a comination of the types `Array`, `Boolean`, `Float`,
    `Integer`, `Null`, `Object`, and `String`.
    """
    TYPE = None
    def make(self, _, __):
        return None

    def __new__(cls):
        return Array() | Boolean() | Float() | Integer() | Null() | \
            Object(free_form=True) | String()
