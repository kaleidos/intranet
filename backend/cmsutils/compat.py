"""
Convenience routines for ensure compatibility.

Some code is Django improvement thats are not included yet into trunk.

"""

from django.db.models.fields.subclassing import Creator


class SubfieldBase(type):
    """
    Modified Django SubfieldBase metaclass to work with field subclasses. See ticket #10728

    A metaclass for custom Field subclasses. This ensures the model's attribute
    has the descriptor protocol attached to it.
    """
    def __new__(cls, base, name, attrs):
        new_class = super(SubfieldBase, cls).__new__(cls, base, name, attrs)
        new_class.contribute_to_class = make_contrib(
                attrs.get('contribute_to_class'), new_class)
        return new_class


def make_contrib(func, field_class):
    """
    Returns a suitable contribute_to_class() method for the Field subclass.

    If 'func' is passed in, it is the existing contribute_to_class() method on
    the subclass and it is called before anything else. It is assumed in this
    case that the existing contribute_to_class() calls all the necessary
    superclass methods.
    """
    def contribute_to_class(self, cls, name):
        if func:
            func(self, cls, name)
        else:
            super(field_class, self).contribute_to_class(cls, name)
        setattr(cls, self.name, Creator(self))

    return contribute_to_class
