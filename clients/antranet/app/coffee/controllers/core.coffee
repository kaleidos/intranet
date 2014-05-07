@HomeCtrl = ($scope, $rootScope, rs) ->
    $rootScope.selectedMenu = "home"

    loadQuote = ->
        success = (data) ->
            $scope.quoteMsg = data.quote
            $scope.quoteAuth = if data.employee_user then data.employee_user.full_name else data.external_author
        rs.getRandomQuote().then(success)

    loadQuote()

@HomeCtrl.$inject = ['$scope', '$rootScope', 'resource']


@LoginCtrl = ($scope, $location, $rootScope, flash, config, rs, storage) ->
    if $rootScope.token_auth
        $location.url('/home')

    $rootScope.selectedMenu = ""
    $scope.status = "login"

    $scope.login = ->
        data = {
            username: $scope.username
            password: $scope.password
        }

        success = (data) ->
            if(data.token?)
                $rootScope.token_auth = data.token
                storage.set('token_auth', data.token)
                storage.set('user_id', data.id)
                $location.url('/home')

        error = (data) ->
            flash([{ level: 'warning', text: data.detail }])

        rs.login(data).then(success, error)

    $scope.recoverPassword = () ->
        data = {
            username: $scope.username
            client_domain: config.client_host
            use_https: config.client_scheme == 'https'
        }

        success = (data) ->
            $scope.status = "recoveredPassword"
            flash([{ level: 'success', text: data.detail }])

        error = (data) ->
            flash([{ level: 'warning', text: data.detail }])

        rs.resetPassword(data).then(success, error)

@LoginCtrl.$inject = ['$scope', '$location', '$rootScope', 'flash', 'antranet.config', 'resource', 'storage']


@LogoutCtrl = ($scope, $location, $rootScope, rs, storage) ->
    $scope.selectedMenu = ""

    success = ->
        $location.url('/login')
        $rootScope.token_auth = null
        storage.set('token_auth', null)

    rs.logout().then(success)

@LogoutCtrl.$inject = ['$scope', '$location', '$rootScope', 'resource', 'storage']


@ResetCtrl = ($rootScope, $scope, $location, $routeParams, flash, rs) ->
    $scope.selectedMenu = ""

    $scope.changePassword = () ->
        data = {
            token: $routeParams.token
            password1: $scope.password1
            password2: $scope.password2
        }

        success = (data) ->
            $location.path('/login')
            flash([{ level: 'success', text: data.detail }])

        error = (data) ->
            flash([{ level: 'warning', text: data.detail }])

        rs.setUserPassword(data).then(success, error)

@ResetCtrl.$inject = ['$rootScope', '$scope', '$location', '$routeParams', 'flash', 'resource']
