@PreferencesCtrl = ($rootScope, $scope, $location, $http, flash, apiUrl) ->
    $rootScope.selectedMenu = "preferences"

    $scope.changePassword = () ->
        if $scope.password1 != $scope.password2
            flash([{ level: 'warning', text: 'Passwords not mach' }])
        else
            $http(
                method: "POST"
                url: apiUrl("change-password")
                headers:
                    "X-SESSION-TOKEN": $rootScope.token_auth
                data:
                    password1: $scope.password1
                    password2: $scope.password2
            ).success((data) ->
                flash([{ level: 'success', text: 'Password changed' }])
            ).error((data) ->
                flash([{ level: 'warning', text: 'Invalid password change' }])
            )

@PreferencesCtrl.$inject = ['$rootScope', '$scope', '$location', '$http', 'flash', 'apiUrl']
