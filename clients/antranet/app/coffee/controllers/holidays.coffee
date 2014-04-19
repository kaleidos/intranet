@HolidaysCtrl = ($scope, $rootScope, rs, $model) ->
    $rootScope.selectedMenu = "holidays"
    $scope.dateOptions = {
        changeYear: true
        changeMonth: true
        dateFormat: "dd/mm/yy"
    }
    $scope.request = {}

    _setHolidayYear = (year) ->
        $scope.year = year
        getHolidaysRequests(year)

    _getHolidaysYears = () ->
        success = (data) ->
            $scope.years = data
            if $scope.year?
                $scope.setHolidayYearById($scope.year.id)
            else
                _setHolidayYear(data[data.length - 1])

        rs.listHolidaysYears().then(success)

    getHolidaysRequests = (year) ->
        success = (data) ->
            $scope.holidays_requests = data
            $rootScope.$broadcast "holidaysReload", $scope

        rs.listHolidaysRequests({year: year.id}).then(success)

    $scope.setHolidayYearById = (yearId) ->
        years = _.filter($scope.years, {id: yearId})
        if years.length == 1
            _setHolidayYear(years[0])

    $scope.sendRequest = ->
        $scope.request.year = $scope.year.id
        $scope.request.beginning = moment($scope.request.beginning).format("YYYY-MM-DD")
        $scope.request.ending = moment($scope.request.ending).format("YYYY-MM-DD")

        success =  ->
            _getHolidaysYears()
            $scope.request = {}

        $model.create("holidays-requests", $scope.request).then(success)

    $scope.deleteRequest = (request) ->
        request.delete().then ->
            _getHolidaysYears()

    $scope.getStatusClass = (status_id) ->
        if (status_id == 0)
            return "status-pending"
        else if (status_id == 10)
            return "status-sent"
        else if (status_id == 20)
            return "status-accepted"
        else if (status_id == 30)
            return "status-rejected"

    $scope.getStatusName = (status_id) ->
        if (status_id == 0)
            return "PENDING"
        else if (status_id == 10)
            return "SENT"
        else if (status_id == 20)
            return "ACCEPTED"
        else if (status_id == 30)
            return "REJECTED"

    _getHolidaysYears()

@HolidaysCtrl.$inject = ["$scope", "$rootScope", "resource", "$model"]
