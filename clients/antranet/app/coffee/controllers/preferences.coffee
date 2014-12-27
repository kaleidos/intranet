module = angular.module("antranet.controllers.preferences", [])


PreferencesCtrl = ($rootScope, $scope, rs, flash) ->
    $rootScope.selectedMenu = "preferences"

    $scope.changePassword = () ->
        data =
            password1: $scope.password1
            password2: $scope.password2

        success = (result) ->
            flash([{ level: 'success', text: result.detail }])

        error = (result) ->
            flash([{ level: 'warning', text: result.detail }])

        rs.setUserPassword(data).then(success, error)

PreferencesCtrl.$inject = ['$rootScope', '$scope', 'resource', 'flash']


module.controller("PreferencesCtrl", PreferencesCtrl)
