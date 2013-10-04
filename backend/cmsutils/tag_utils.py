from django import template
from django.utils.encoding import smart_str
from django.template.loader import render_to_string


def parse_args_kwargs_and_as_var(parser, token):
    """
    Parse uniformly args and kwargs from a templatetag

    Usage::

      For parsing a template like this:

      {% footag my_contents,height=10,zoom=20 as myvar %}

      You simply do this:

      @register.tag
      def footag(parser, token):
          args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, token)
    """
    bits = token.contents.split(' ')

    if len(bits) <= 1:
        raise template.TemplateSyntaxError("'%s' takes at least one argument" % bits[0])

    args = []
    kwargs = {}
    as_var = None

    bits = iter(bits[1:])
    for bit in bits:
        if bit == 'as':
            as_var = bits.next()
            break
        else:
            for arg in bit.split(","):
                if '=' in arg:
                    k, v = arg.split('=', 1)
                    k = k.strip()
                    kwargs[k] = template.Variable(v)
                elif arg:
                    args.append(template.Variable(arg))
    return args, kwargs, as_var


def get_args_and_kwargs(args, kwargs, context):
    out_args = [arg.resolve(context) for arg in args]
    out_kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context)) for k, v in kwargs.items()])
    return out_args, out_kwargs


class RenderWithArgsAndKwargsNode(template.Node):
    """
    Node for templatetags which renders templates with parsed args and kwargs

    Usage::

      class FooNode(RenderWithArgsAndKwargsNode):
          def prepare_context(self, context, args, kwargs):
              context['result_list'] = kwargs['result_list']
              return context

      @register.tag
      def footag(parser, token):
          args, kwargs, as_var = parse_args_kwargs_and_as_var(parser, token)
          return FooNode(args, kwargs, template='footag.html')
    """

    def __init__(self, args, kwargs, template):
        self.args = args
        self.kwargs = kwargs
        self.template = template

    def prepare_context(self, args, kwargs, context):
        """
        Hook for overriding in subclasses.

        Note that "args" and "kwargs" parameters are already resolved with context
        """
        return context

    def render(self, context):
        args, kwargs = get_args_and_kwargs(self.args, self.kwargs, context)
        context = self.prepare_context(args, kwargs, context)
        return render_to_string(self.template, context)