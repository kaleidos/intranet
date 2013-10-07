@TalksCtrl = ($scope, $rootScope, $http, apiUrl) ->
    $scope.currentPage = 1

    $rootScope.selectedMenu = "talks"

    loadTalks = () ->
        $http(
            method: "GET"
            url: apiUrl('talks')
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
            params:
                "page": $scope.currentPage
                "page_size": 15
        ).success((data) ->
            $scope.talks = data['results']
            $scope.hasNext = data['next'] != null
            $scope.hasPrev = data['previous'] != null
            $scope.pages = [1..((data['count']/15)+1)]
        )

    $scope.nextPage = () ->
        $scope.currentPage = $scope.currentPage + 1
        loadParts()

    $scope.prevPage = () ->
        $scope.currentPage = $scope.currentPage - 1
        loadParts()

    $scope.selectPage = (page) ->
        $scope.currentPage = page
        loadParts()

    loadTalks()
@TalksCtrl.$inject = ['$scope', '$rootScope', '$http', 'apiUrl']
