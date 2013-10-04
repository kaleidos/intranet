from django.forms import ModelForm

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

__all__ = (
    'GenericForm',
    'GenericAddForm',
    'GenericEditForm',
)

class GenericForm(ModelForm):
    """ Base form that simplify use of ModelForms """

    template = None

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(GenericForm, self).__init__(*args, **kwargs)

    def update(self):
        """Validate and save the data if we are bound

        You can redefine this method and do other interesting stuff like
        sending an email for the typical unbound contact form.
        """
        if self.is_bound and self.is_valid():
            return self.save()

    def next_url(self, obj):
        """Return the url where we should go if everything went ok after
        updating a bound form.

        Subclasses must redefine this.
        """
        if hasattr(obj, 'get_absolute_url'):
            return obj.get_absolute_url()
        return '../'

    def run(self, **extra_context):
        """The run method ecapsulated the most common logic for a form:

         * First update the form (validate and create/update the context)
         * Then render the form and return the output

        """

        obj = self.update()
        if obj is not None:
            return HttpResponseRedirect(self.next_url(obj))

        context = extra_context

        context['form'] = self
        context['object'] = self.instance

        return render_to_response(self.template, context,
                                  context_instance = RequestContext(self.request))


class GenericAddForm(GenericForm):
    """ Base class for all adding object forms

    Example use:
    >>> from django.db import models
    >>> class Author(models.Model):
    ...     name = models.CharField(max_length=100)
    ...     description = models.CharField(max_length=500)
    ...
    >>> class AuthorAddForm(GenericAddForm):
    ...     template = 'authors/add.html'
    ...     class Meta:
    ...         model = Author
    ...         fields = ('name', 'description',)
    ...
    >>> def add(request):
    ...     form = AuthorAddForm(request)
    ...     return form.run()
    ...

    The key is the last form() line from a view. The behaviour is:
     - in GET request, render template attribute with form in context
     - in POST creates objects and redirect to result of form.next_url() or
       fails if there are errors and repeat rendering form in template
    """
    def __init__(self, request, *args, **kwargs):
        if request.POST:
            super(GenericAddForm, self).__init__(request,
                                                 request.POST,
                                                 request.FILES,
                                                 *args,
                                                 **kwargs)
        else:
            super(GenericAddForm, self).__init__(request,
                                                 *args,
                                                 **kwargs)



class GenericEditForm(GenericForm):
    """ Base class for all editing object forms

    Example use:

    >>> from django.db import models
    >>> class Author(models.Model):
    ...     name = models.CharField(max_length=100)
    ...     description = models.CharField(max_length=500)
    ...
    >>> class AuthorEditForm(GenericAddForm):
    ...     template = 'authors/edit.html'
    ...     class Meta:
    ...         model = Author
    ...         fields = ('name', 'description',)
    ...
    >>> def edit(request, author_id):
    ...     author = get_object_or_404(Author, pk=author_id)
    ...     form = AuthorEditForm(request, author)
    ...     return form.run()
    ...

    Behaviour is exactly the same as GenericAddForm, but with object bound
    """
    def __init__(self, request, instance, *args, **kwargs):
        if request.method == 'POST':
            super(GenericEditForm, self).__init__(request,
                                                  request.POST,
                                                  request.FILES,
                                                  instance=instance,
                                                  *args,
                                                  **kwargs)
        else:
            super(GenericEditForm, self).__init__(request,
                                                  instance=instance,
                                                  *args,
                                                  **kwargs)
