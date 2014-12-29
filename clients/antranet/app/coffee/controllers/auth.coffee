antranet = @.antranet
bindMethods = antranet.bindMethods

module = angular.module("antranet.controllers.auth", [])


##########################################################
## Login Controller
##########################################################

class LoginCtrl extends antranet.Controller
    @.$inject = [
        '$rootScope',
        '$scope',
        '$location',
        'storage',
        'flash',
        'antranet.config',
        'resource'
    ]

    constructor:  (@rootScope, @scope, @location, @storage, @flash, @config, @rs) ->
        bindMethods(@)

        @rootScope.selectedMenu = ""

        if @rootScope.token_auth
            @location.url('/home')

        @scope.status = "login"

    login: ->
        data = {
            username: @scope.username
            password: @scope.password
        }

        success = (data) =>
            if data.token?
                @rootScope.token_auth = data.token
                @storage.set('token_auth', data.token)
                @storage.set('user_id', data.id)
                @location.url('/home')

        error = (data) =>
            @flash([{ level: 'warning', text: data.detail }])

        @rs.login(data).then(success, error)

    recoverPassword: ->
        data = {
            username: @scope.username
            client_domain: @config.client_host
            use_https: @config.client_scheme == 'https'
        }

        success = (data) =>
            @scope.status = "recoveredPassword"
            @flash([{ level: 'success', text: data.detail }])

        error = (data) =>
            @flash([{ level: 'warning', text: data.detail }])

        @rs.resetPassword(data).then(success, error)

module.controller("LoginCtrl", LoginCtrl)


##########################################################
## Logout Controller
##########################################################

class LogoutCtrl extends antranet.Controller
    @.$inject = [
        '$rootScope',
        '$scope',
        '$location',
        'storage',
        'resource'
    ]

    constructor:  (@rootScope, @scope, @location, @storage, @rs) ->
        bindMethods(@)

        @scope.selectedMenu = ""
        @.logout()

    logout: ->
        success = =>
            @location.url('/login')
            @rootScope.token_auth = null
            @storage.set('token_auth', null)

        @rs.logout().then(success)

module.controller("LogoutCtrl", LogoutCtrl)


##########################################################
## Change password Controller
##########################################################

class ResetCtrl extends antranet.Controller
    @.$inject = [
        '$rootScope',
        '$scope',
        '$location',
        '$routeParams',
        'flash',
        'resource'
    ]

    constructor:  (@rootScope, @scope, @location, @routeParams, @flash, @rs) ->
        bindMethods(@)

        @scope.selectedMenu = ""

    changePassword: ->
        data = {
            token: @routeParams.token
            password1: @scope.password1
            password2: @scope.password2
        }

        success = (data) =>
            @location.path('/login')
            @flash([{ level: 'success', text: data.detail }])

        error = (data) =>
            @flash([{ level: 'warning', text: data.detail }])

        @rs.setUserPassword(data).then(success, error)

module.controller("ResetCtrl", ResetCtrl)
