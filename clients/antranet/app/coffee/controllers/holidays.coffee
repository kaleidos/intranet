@HolidaysCtrl = ($scope, $rootScope, $http, apiUrl) ->
    $rootScope.selectedMenu = "holidays"
    $scope.dateOptions = {
        changeYear: true
        changeMonth: true
        dateFormat: 'dd/mm/yy'
    }
    $scope.request = {}

    getHolidaysYears = () ->
        $http(
            method: "GET"
            url: apiUrl('holidays-years')
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
            params:
                page_size: 0
        ).success((data) ->
            $scope.years = data
            if $scope.year?
                $scope.setHolidayYearById($scope.year.id)
            else
                setHolidayYear(data[data.length - 1])
        )

    getHolidaysRequests = (year) ->
        $http(
            method: "GET"
            url: apiUrl('holidays-requests')
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
            params:
                page_size: 0
                year: year.id
        ).success((data) ->
            $scope.holidays_requests = data
            $rootScope.$broadcast "holidaysReload", $scope
        )

    setHolidayYear = (year) ->
        $scope.year = year
        getHolidaysRequests(year)

    $scope.setHolidayYearById = (yearId) ->
        years = _.filter($scope.years, {id: yearId})
        if years.length == 1
            setHolidayYear(years[0])

    $scope.sendRequest = ->
        holidayRequest =
            'beginning': moment($scope.request.beginning).format("YYYY-MM-DD")
            'ending': moment($scope.request.ending).format("YYYY-MM-DD")
            'flexible_dates': $scope.request.flexibleDates
            'comments': $scope.request.comments
            'year': $scope.year.id

        $http(
            method: "POST"
            url: apiUrl('holidays-requests')
            data: holidayRequest
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
        ).success((data) ->
            getHolidaysYears()
            $scope.request = {}
        )

    $scope.deleteRequest = (requestId) ->
        $http(
            method: "DELETE"
            url: "#{apiUrl('holidays-requests')}#{requestId}/"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
        ).success((data) ->
            getHolidaysYears()
        )

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

    getHolidaysYears()

@HolidaysCtrl.$inject = ['$scope', '$rootScope', '$http', 'apiUrl']
