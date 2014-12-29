@.antranet = {} if not @.antranet

configCallback = ($routeProvider, $locationProvider, $httpProvider, $provide) ->
    $routeProvider.when("/login", {templateUrl: "/partials/login.html"})
    $routeProvider.when("/logout", {templateUrl: "/partials/logout.html"})
    $routeProvider.when("/reset/:token", {templateUrl: "/partials/reset.html"})
    $routeProvider.when("/home", {templateUrl: "/partials/home.html"})
    $routeProvider.when("/parts", {templateUrl: "/partials/parts.html"})
    $routeProvider.when("/parts/:id", {templateUrl: "/partials/part.html"})
    $routeProvider.when("/holidays", {templateUrl: "/partials/holidays.html"})
    $routeProvider.when("/talks", {templateUrl: "/partials/talks.html"})
    $routeProvider.when("/quotes", {templateUrl: "/partials/quotes.html"})
    $routeProvider.when("/preferences", {templateUrl: "/partials/preferences.html"})
    $routeProvider.otherwise({redirectTo: "/login"})

    $locationProvider.html5Mode({enabled: true, requireBase: false})

    defaultHeaders = {
        "Content-Type": "application/json"
        "Accept-Language": "en"
    }
    $httpProvider.defaults.headers.delete = defaultHeaders
    $httpProvider.defaults.headers.patch = defaultHeaders
    $httpProvider.defaults.headers.post = defaultHeaders
    $httpProvider.defaults.headers.put = defaultHeaders

    authHttpIntercept =  ($q, $location, $rootScope, storage) ->
        responseError = (response) ->
            if (response.status == 401 or response.status == 403)
                $location.url("/login")
                $rootScope.token_auth = ""
                storage.set("token_auth", "")
            return $q.reject(response)

        return {responseError: responseError}

    $provide.factory("authHttpIntercept", ["$q", "$location", "$rootScope", "storage", authHttpIntercept])
    $httpProvider.interceptors.push("authHttpIntercept")


init = ($rootScope, $location, storage) ->
    $rootScope.token_auth = storage.get("token_auth")
    $rootScope.user_id = storage.get("user_id")
    $rootScope._ = _

modules = [
    "ngRoute"
    "ngSanitize"
    "antranet.controllers.auth"
    "antranet.controllers.holidays"
    "antranet.controllers.home"
    "antranet.controllers.parts"
    "antranet.controllers.preferences"
    "antranet.controllers.quotes"
    "antranet.controllers.talks"
    "antranet.filters"
    "antranet.services.common"
    "antranet.services.storage"
    "antranet.services.apiurl"
    "antranet.services.model"
    "antranet.services.resource"
    "antranet.directives.holidays"
    "antranet.directives.vimdings"
    "antranet.directives.autofill"
    "antranet.directives.ui"
    "flash"
    "ui"
]

# Declare app level module which depends on filters, and services
module = angular.module("antranet", modules)

module.config([
    "$routeProvider",
    "$locationProvider",
    "$httpProvider",
    "$provide",
    configCallback
])

module.run([
    "$rootScope",
    "$location",
    "storage",
    init
])

module.value("ui.config", {
    date: { firstDay: 1 }
})
