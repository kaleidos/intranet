@antranet = {} if not @antranet

configCallback = ($routeProvider, $httpProvider, $provide, $compileProvider) ->
    $routeProvider.when('/login', {templateUrl: 'partials/login.html', controller: LoginCtrl})
    $routeProvider.when('/logout', {templateUrl: 'partials/logout.html', controller: LogoutCtrl})
    $routeProvider.when('/reset/:token', {templateUrl: 'partials/reset.html', controller: ResetCtrl})
    $routeProvider.when('/home', {templateUrl: 'partials/home.html', controller: HomeCtrl})
    $routeProvider.when('/parts', {templateUrl: 'partials/parts.html', controller: PartsCtrl})
    $routeProvider.when('/parts/:id', {templateUrl: 'partials/part.html', controller: PartCtrl})
    $routeProvider.when('/holidays', {templateUrl: 'partials/holidays.html', controller: HolidaysCtrl})
    $routeProvider.when('/talks', {templateUrl: 'partials/talks.html', controller: TalksCtrl})
    $routeProvider.when('/quotes', {templateUrl: 'partials/quotes.html', controller: QuotesCtrl})
    $routeProvider.when('/preferences', {templateUrl: 'partials/preferences.html', controller: PreferencesCtrl})
    $routeProvider.otherwise({redirectTo: '/login'})

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
