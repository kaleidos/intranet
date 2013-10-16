@antranet = {} if not @antranet

configCallback = ($routeProvider, $httpProvider, $provide, $compileProvider) ->
    $routeProvider.when('/login', {templateUrl: 'partials/login.html', controller: LoginCtrl})
    $routeProvider.when('/logout', {templateUrl: 'partials/logout.html', controller: LogoutCtrl})
    $routeProvider.when('/reset/:token', {templateUrl: 'partials/reset.html', controller: ResetCtrl})
    $routeProvider.when('/preferences', {templateUrl: 'partials/preferences.html', controller: PreferencesCtrl})
    $routeProvider.when('/home', {templateUrl: 'partials/home.html', controller: HomeCtrl})
    $routeProvider.when('/parts', {templateUrl: 'partials/parts.html', controller: PartsCtrl})
    $routeProvider.when('/parts/:id', {templateUrl: 'partials/part.html', controller: PartCtrl})
    $routeProvider.when('/talks', {templateUrl: 'partials/talks.html', controller: TalksCtrl})
    $routeProvider.when('/holidays', {templateUrl: 'partials/holidays.html', controller: HolidaysCtrl})
    $routeProvider.otherwise({redirectTo: '/login'})

    defaultHeaders =
        "Content-Type": "application/json"

    $httpProvider.defaults.headers.delete = defaultHeaders
    $httpProvider.defaults.headers.patch = defaultHeaders
    $httpProvider.defaults.headers.post = defaultHeaders
    $httpProvider.defaults.headers.put = defaultHeaders

    $provide.factory("authHttpIntercept", ["$q", "$location", ($q, $location) ->
        return (promise) ->
            return promise.then null, (response) ->
                if (response.status == 401)
                    $location.url("/login")
                    $rootScope.token_auth = ''
                    storage.set('token_auth', '')
                else if (response.status == 403)
                    $location.url("/login")
                    $rootScope.token_auth = ''
                    storage.set('token_auth', '')
                return $q.reject(response)
    ])

    $compileProvider.urlSanitizationWhitelist(/^\s*(https?|ftp|mailto|file|blob):/)
    $httpProvider.responseInterceptors.push('authHttpIntercept')

init = ($rootScope, $location, storage) ->
    $rootScope.token_auth = storage.get('token_auth')
    $rootScope.user_id = storage.get('user_id')
    $rootScope._ = _

modules = [
    'antranet.filters'
    'antranet.services.common'
    'antranet.services.storage'
    'antranet.services.apiurl'
    'antranet.directives.holidays'
    'antranet.directives.vimdings'
    'flash'
    'ui'
]

# Declare app level module which depends on filters, and services
angular.module('antranet', modules)
    .config(['$routeProvider', '$httpProvider', '$provide', '$compileProvider', configCallback])
    .run(['$rootScope', '$location', 'storage', init])
    .value('ui.config', {
        date: {
            firstDay: 1
        }
    })
