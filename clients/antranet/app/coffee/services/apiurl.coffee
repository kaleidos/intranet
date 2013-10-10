angular.module 'antranet.services.apiurl', ['antranet.config'], ($provide) ->
    apiUrlProvider = (config) ->
        urls =
            "login": "/api/v1/auth/login/"
            "logout": "/api/v1/auth/logout/"
            "reset-password": "/api/v1/auth/reset-password/"
            "change-password": "/api/v1/auth/change-password/"
            "parts": "/api/v1/parts/"
            "talks": "/api/v1/talks/"
            "projects": "/api/v1/projects/"
            "holidays-years": "/api/v1/holidays-years/"
            "holidays-requests": "/api/v1/holidays-requests/"
            "holidays": "/api/v1/holidays/"
            "special-days": "/api/v1/special-days/"

        host = config.host or "localhost:8000"
        scheme = config.scheme or "http"

        return () ->
            args = _.toArray(arguments)
            name = args.slice(0, 1)
            params = [urls[name]]

            for item in args.slice(1)
                params.push(item)

            url = _.str.sprintf.apply(null, params)
            return _.str.sprintf("%s://%s%s", scheme, host, url)

    $provide.factory("apiUrl", ['antranet.config', apiUrlProvider])
