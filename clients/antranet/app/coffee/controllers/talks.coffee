@TalksCtrl = ($scope, $rootScope, $http, apiUrl) ->
    $scope.currentPage = 1
    $scope.ordering = "-created_date"
    $scope.newTalk = {}

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
                "ordering": $scope.ordering
        ).success((data) ->
            $scope.talks = data['results']
            $scope.hasNext = data['next'] != null
            $scope.hasPrev = data['previous'] != null
            $scope.pages = [1..((data['count']/15)+1)]
        )

    $scope.addTalk = () ->
        $http(
            method: "POST"
            url: "#{apiUrl('talks')}"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
            data: $scope.newTalk
        ).success((data) ->
            loadTalks()
            $scope.newTalk = {}
            $scope.newTalkForm = false
        )

    $scope.iWant = (id) ->
        $http(
            method: "POST"
            url: "#{apiUrl('talks')}#{id}/i_want/"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
        ).success((data) ->
            loadTalks()
        )

    $scope.iNotWant = (id) ->
        $http(
            method: "DELETE"
            url: "#{apiUrl('talks')}#{id}/i_want/"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
        ).success((data) ->
            loadTalks()
        )

    $scope.iNotTalk = (id) ->
        $http(
            method: "DELETE"
            url: "#{apiUrl('talks')}#{id}/i_talk/"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
        ).success((data) ->
            loadTalks()
        )

    $scope.iTalk = (id) ->
        $http(
            method: "POST"
            url: "#{apiUrl('talks')}#{id}/i_talk/"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
        ).success((data) ->
            loadTalks()
        )

    $scope.iTalkersAreReady = (talk) ->
        if _.any(talk.talkers, {'id': $rootScope.user_id})
            $http(
                method: "POST"
                url: "#{apiUrl('talks')}#{talk.id}/i_talkers_are_ready/"
                headers:
                    "X-SESSION-TOKEN": $rootScope.token_auth
            ).success((data) ->
                loadTalks()
            )

    $scope.iTalkersAreNotReady = (talk) ->
        if _.any(talk.talkers, {'id': $rootScope.user_id})
            $http(
                method: "POST"
                url: "#{apiUrl('talks')}#{talk.id}/i_talkers_are_not_ready/"
                headers:
                    "X-SESSION-TOKEN": $rootScope.token_auth
            ).success((data) ->
                loadTalks()
            )

    $scope.talkStatus = (talk) ->
        # red    - There are no talkers yet
        # yellow - There are talkers but they are not ready
        # green  - The talkers are ready
        if talk.talkers.length > 0
            if talk.talkers_are_ready
                return "green"
            return "yellow"
        return "red"

    $scope.setOrder = (order) ->
        $scope.currentPage = 1
        $scope.ordering = order
        loadTalks()

    $scope.nextPage = () ->
        $scope.currentPage = $scope.currentPage + 1
        loadTalks()

    $scope.prevPage = () ->
        $scope.currentPage = $scope.currentPage - 1
        loadTalks()

    $scope.selectPage = (page) ->
        $scope.currentPage = page
        loadTalks()

    loadTalks()
@TalksCtrl.$inject = ['$scope', '$rootScope', '$http', 'apiUrl']
