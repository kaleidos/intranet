@TalksCtrl = ($scope, $rootScope, rs, $model) ->
    $scope.currentPage = 1
    $scope.ordering = "-created_date"
    $scope.newTalk = {}

    $rootScope.selectedMenu = "talks"

    loadTalks = () ->
        params = {
            page: $scope.currentPage
            page_size: 15
            ordering: $scope.ordering
        }
        rs.listPaginatedTalks(params).then (data) ->
            $scope.talks = data.models
            $scope.hasNext = data.next != null
            $scope.hasPrev = data.prev != null
            $scope.pages = [1.. ((data.count/15) + 1)]

    $scope.addTalk = () ->
        $model.create("talks", $scope.newTalk).then ->
            loadTalks()
            $scope.newTalk = {}
            $scope.newTalkForm = false

    $scope.iWant = (talk) ->
        rs.setTalkIWant(talk.id).then ->
            loadTalks()

    $scope.iNotWant = (talk) ->
        rs.setTalkINotWant(talk.id).then ->
            loadTalks()

    $scope.iTalk = (talk) ->
        rs.setTalkITalk(talk.id).then ->
            loadTalks()

    $scope.iNotTalk = (talk) ->
        rs.setTalkINotTalk(talk.id).then ->
            loadTalks()

    $scope.iTalkersAreReady = (talk) ->
        if _.any(talk.talkers, {"id": $rootScope.user_id})
            rs.setTalkersAreReady(talk.id).then ->
                loadTalks()

    $scope.iTalkersAreNotReady = (talk) ->
        if _.any(talk.talkers, {"id": $rootScope.user_id})
            rs.setTalkersAreNotReady(talk.id).then ->
                loadTalks()

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

@TalksCtrl.$inject = ["$scope", "$rootScope", "resource", "$model"]
