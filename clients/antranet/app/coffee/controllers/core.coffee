@LoginCtrl = ($scope, $http, $location, $rootScope, flash, config, apiUrl, storage) ->
    $rootScope.selectedMenu = ""
    $scope.status = "login"
    $scope.login = () ->
        $http(
            method: "POST"
            url: apiUrl("login")
            data:
                username: $scope.username
                password: $scope.password
        ).success((data) ->
            if(data.token?)
                $rootScope.token_auth = data.token
                storage.set('token_auth', data.token)
                storage.set('user_id', data.id)
                $location.url('/home')
        ).error((data) ->
            flash([{ level: 'warning', text: 'Invalid username or password' }])
        )

    $scope.recoverPassword = () ->
        $http(
            method: "POST"
            url: apiUrl("reset-password")
            data:
                username: $scope.username
                client_domain: config.client_host
                use_https: config.client_scheme == 'https'
        ).success((data) ->
            $scope.status = "recoveredPassword"
            flash([{ level: 'success', text: 'Password recover email sent' }])
        ).error((data) ->
            flash([{ level: 'warning', text: 'Invalid username' }])
        )
@LoginCtrl.$inject = ['$scope', '$http', '$location', '$rootScope', 'flash', 'antranet.config', 'apiUrl', 'storage']

@LogoutCtrl = ($scope, $http, $location, $rootScope, apiUrl, storage) ->
    $scope.selectedMenu = ""
    $http(
        method: "POST"
        url: apiUrl("logout")
    ).success((data) ->
        $location.url('/login')
        $rootScope.token_auth = null
        storage.set('token_auth', null)
    )
@LogoutCtrl.$inject = ['$scope', '$http', '$location', '$rootScope', 'apiUrl', 'storage']

@ResetCtrl = ($rootScope, $scope, $location, $routeParams, $http, flash, apiUrl) ->
    $scope.selectedMenu = ""

    $scope.changePassword = () ->
        if $scope.password1 != $scope.password2
            flash([{ level: 'warning', text: 'Passwords not mach' }])
        else
            $http(
                method: "POST"
                url: apiUrl("change-password")
                data:
                    token: $routeParams.token
                    password1: $scope.password1
                    password2: $scope.password2
            ).success((data) ->
                $location.path('/login')
                flash([{ level: 'success', text: 'Password changed' }])
            ).error((data) ->
                flash([{ level: 'warning', text: 'Invalid password change' }])
            )

@ResetCtrl.$inject = ['$rootScope', '$scope', '$location', '$routeParams', '$http', 'flash', 'apiUrl']

@HomeCtrl = ($rootScope) ->
    $rootScope.selectedMenu = "home"
@HomeCtrl.$inject = ['$rootScope']
