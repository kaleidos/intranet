from django import template
from django.template import Library
from django.template import resolve_variable

register = Library()


BASIC_TEMPLATE = """<img id="%(id)s" src="%(url)s" width="%(width)spx" height="%(height)spx" class="%(css)s" />"""
URL_TEMPLATE = "http://maps.google.com/staticmap?center=%(latitude)s,%(longitude)s&zoom=%(zoom)s&size=%(width)sx%(height)s&maptype=%(maptype)s&markers=%(markers)s&key=%(api_key)s"
# {% static-gmap id:'mymap' title:'Alternative text to map' width:'300' height:'300' latitude:'x' longitude:'y' zoom:'20' maptype:'mobile' marker:(x,y,color,letter) css:'my-css-class' api_key:'FJGASD...ASDFASDF' %}

class StaticGMapNode (template.Node):
    def __init__(self, params):
        self.params = params
        self.markers = []
    
    def get_marker(self, str, context):

        args = [i.strip() for i in str[1:-1].split(",")]
        x, y, color, letter = tuple(args)

        return {'x':self.resolve_variable(x, context), 'y':self.resolve_variable(y, context), 'color':self.resolve_variable(color, context), 'letter':self.resolve_variable(letter, context)}
    
    def render_markers(self):     
        return "%".join( ["%(x)s,%(y)s,%(color)s%(letter)s" % i for i in self.markers] )
    
    def resolve_variable(self, var, context):
        parts = var.split(".")
        try:
            obj = resolve_variable(parts[0], context)

            for p in parts[1:]:
                obj = getattr(obj, p)

            return obj
        except:
            return var
    
    def render (self, context):
        for k,v in self.params.items():
            if k=="marker":
                self.markers.append( self.get_marker(v, context) )
            else:
                try:
                    if v[0] in ("\"", "(", "[", "'"):
                        v = v[1:-1]
                    else:
                        v = self.resolve_variable(v, context)
                    self.params[k] = v
                except:
                    self.params[k] = v

        self.params["markers"] = self.render_markers()
        self.params["url"] = URL_TEMPLATE % self.params

        return BASIC_TEMPLATE % self.params

def do_static_gmap(parser, token):
    items = token.split_contents()
   
    #Default values 
    parameters={
            'id'        : 'default',
            'title'     : 'Default alternative text',
            'width'     : '300',
            'height'    : '300',
            'latitude'  : '33',
            'longitude' : '-3',
            'zoom'      : '15',
            'maptype'   : 'mobile', # roadmap, mobile
            'css'       : '',
            'api_key'   : '',            
            'marker'    : '(0,0,blue,s)',
            'markers'   : [],
    }
    for item in items[1:]:
        param, value = item.split(":")
        param = param.strip()
        value = value.strip()
        
        if parameters.has_key(param):
            parameters[param] = value
        
    return StaticGMapNode(parameters)

register.tag('static-gmap', do_static_gmap)


