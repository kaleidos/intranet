from fields import SlugField, ButtonField, ESCCCField, LatitudeLongitudeField
from forms import GenericForm, GenericAddForm, GenericEditForm

# stupid hack to make pyflakes happier
unused_imports = (SlugField, ButtonField, ESCCCField, LatitudeLongitudeField,
                  GenericForm, GenericAddForm, GenericEditForm)