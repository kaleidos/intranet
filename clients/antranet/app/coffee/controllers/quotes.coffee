@QuotesCtrl = ($scope, $rootScope, rs, $model, $window) ->
    $scope.currentPage = 1
    $scope.ordering = "-created_date"
    $scope.newQuote = {}

    $rootScope.selectedMenu = "quotes"

    loadQuotes = () ->
        params = {
            page: $scope.currentPage
            page_size: 15
            ordering: $scope.ordering
        }

        rs.listUsers().then (data) ->
            $scope.employees = data

            rs.listPaginatedQuotes(params).then (data) ->
                $scope.quotes = data.models
                $scope.hasNext = data.next != null
                $scope.hasPrev = data.prev != null
                $scope.pages = [1.. ((data.count/15) + 1)]

    $scope.addQuote = () ->
        success = ->
            loadQuotes()
            $scope.newQuote = {}
            $scope.newQuoteForm = false

        $model.create("quotes", $scope.newQuote).then(success)

    $scope.editQuote = (quote) ->
        if $window.confirm("Are you sure you want to apply this changes?")
            quote.save().then ->
                loadQuotes()

    $scope.deleteQuote = (quote) ->
        if $window.confirm("Are you sure you want to delete it?")
            quote.delete().then ->
                loadQuotes()

    $scope.setOrder = (order) ->
        $scope.currentPage = 1
        $scope.ordering = order
        loadQuotes()

    $scope.nextPage = () ->
        $scope.currentPage = $scope.currentPage + 1
        loadQuotes()

    $scope.prevPage = () ->
        $scope.currentPage = $scope.currentPage - 1
        loadQuotes()

    $scope.selectPage = (page) ->
        $scope.currentPage = page
        loadQuotes()

    loadQuotes()

@QuotesCtrl.$inject = ["$scope", "$rootScope", "resource", "$model", "$window"]
