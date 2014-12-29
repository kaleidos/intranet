antranet = @.antranet
bindMethods = antranet.bindMethods

module = angular.module("antranet.controllers.home", [])


##########################################################
## Home Controller
##########################################################

class HomeCtrl extends antranet.Controller
    @.$inject = [
        '$rootScope',
        '$scope',
        'resource'
    ]

    constructor: (@rootScope, @scope, @rs) ->
        bindMethods(@)

        @rootScope.selectedMenu = "home"
        @.loadQuote()

    loadQuote: ->
        success = (data) =>
            @scope.quote = {
                msg: data.quote
                auth: if data.employee_user then data.employee_user.full_name else data.external_author
            }

        @rs.getRandomQuote().then(success)

module.controller("HomeCtrl", HomeCtrl)
