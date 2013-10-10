angular.module('antranet.services.storage', ['antranet.config'], ($provide) ->
    $provide.factory('storage', ['$rootScope', ($rootScope) ->
        service = {}
        helpers = {}

        service.get = (key) ->
            serializedValue = localStorage.getItem(key)
            if (serializedValue == null)
                return serializedValue

            return JSON.parse(serializedValue)

        service.set = (key, val) ->
            if (_.isObject(key))
                _.each key, (val, key) ->
                    service.set(key, val)
            else
                localStorage.setItem(key, JSON.stringify(val))

        service.remove = (key) ->
            localStorage.removeItem(key)

        service.clear = ->
            localStorage.clear()

        return service
    ])
)
