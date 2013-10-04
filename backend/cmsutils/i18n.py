from django.conf import settings
LANGUAGES = settings.LANGUAGES

def get_language_code_list():
    return [lang[0] for lang in LANGUAGES]

def rotate_language(request, response):
    lang_list = get_language_code_list()
    if hasattr(request, 'session'):
        lang_code = request.session.get('django_language', None)
        if not lang_code:
            lang_code = request.LANGUAGE_CODE
        # Rotate from the list
        lang_code = lang_list[(lang_list.index(lang_code)+1)%len(lang_list)]
        request.session['django_language'] = lang_code
    else:
        lang_code = request.get_cookie('django_language')
        # Rotate from the list
        lang_code = lang_list[(lang_list.index(lang_code)+1)%len(lang_list)]
        response.set_cookie('django_language', lang_code)
    return lang_code
