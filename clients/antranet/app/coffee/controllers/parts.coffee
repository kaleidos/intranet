@PartsCtrl = ($scope, $rootScope, $http, apiUrl) ->
    $scope.currentPage = 1

    $rootScope.selectedMenu = "parts"

    loadParts = () ->
        $http(
            method: "GET"
            url: apiUrl('parts')
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
            params:
                "page": $scope.currentPage
                "page_size": 15
        ).success((data) ->
            $scope.parts = data['results']
            $scope.hasNext = data['next'] != null
            $scope.hasPrev = data['previous'] != null
            $scope.pages = [1..((data['count']/15)+1)]
        )

    $scope.sendPart = (partId) ->
        $http(
            method: "POST"
            url: "#{apiUrl('parts')}#{partId}/send/"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
        ).success((data) ->
            loadParts()
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

    loadParts()
@PartsCtrl.$inject = ['$scope', '$rootScope', '$http', 'apiUrl']

@PartCtrl = ($scope, $rootScope, $http, $routeParams, $location, apiUrl, storage) ->
    $rootScope.selectedMenu = "parts"
    $scope.imputations = {}
    $scope.holidays = {}

    week_days = [ 'D', 'L', 'M', 'X', 'J', 'V', 'S' ]
    $scope.showingAll = false

    buildDaysList = (year, month, special_days) ->
        days = []

        day = moment("#{year}-#{month}-01", "YYYY-M-DD")
        month_end = moment("#{year}-#{month}-01", "YYYY-M-DD")
        month_end.add('months', 1)
        just_spacial_days = (special_day.date.day for special_day in special_days)

        while day < month_end
            isSpecial = $.inArray(day.date(), just_spacial_days) != -1
            days.push {
                number: day.date()
                week: week_days[day.day()]
                isSpecial: isSpecial
            }
            day.add('days', 1)
        return days

    loadPart = (partId) ->
        $http(
            method: "GET"
            url: "#{apiUrl('parts')}#{partId}/"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth
        ).success((data) ->
            $scope.part = data

            $scope.special_days = data.special_days

            $scope.days = buildDaysList(data.year, data.month, data.special_days)

            $scope.imputations = data.data
            for project in _.values($scope.projects)
                if not $scope.imputations[project.id]?
                    $scope.imputations[project.id] = {}
                    for day in $scope.days
                        $scope.imputations[project.id][day.number] = 0

            loadHolidays()
            setTimeout(() ->
                $('span.day-imputation input')[0].focus()
            , 100)
        )

    loadProjects = () ->
        $http(
            method: "GET"
            url: apiUrl('projects')
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth,
        ).success((data) ->
            $scope.projects = {}
            for project in data
                $scope.projects[project.id] = project
            loadPart($routeParams.id)
        )

    loadHolidays = () ->
        $http(
            method: "GET"
            url: apiUrl('holidays')
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth,
            params:
                "page_size": 0
                "year": $scope.part.year
                "month": $scope.part.month
        ).success((data) ->
            $scope.holidays = {}
            for day in $scope.days
                $scope.holidays[day.number] = 0
            for date in data
                $scope.holidays[date.day] = 8
                $scope.days[date.day-1].isSpecial = true
        )

    $scope.savePart = () ->
        if $scope.part.state == 10
            return null

        data = $scope.part
        data.data = $scope.imputations

        $http(
            method: "PUT"
            url: "#{apiUrl('parts')}#{data.id}/"
            headers:
                "X-SESSION-TOKEN": $rootScope.token_auth,
            data: data
        ).success((data) ->
            $location.url('/parts')
        )

    $scope.sum = (obj) ->
        if (!$.isArray(obj) or obj.length == 0)
            return 0
        return _.reduce obj, (sum, n) ->
            return sum += parseFloat(n)

    $scope.hide = (projectId) ->
        storage.set("hidden#{projectId}", true)

    $scope.show = (projectId) ->
        storage.set("hidden#{projectId}", false)

    $scope.isHidden = (projectId) ->
        return storage.get("hidden#{projectId}") == true

    $scope.hideAll = () ->
        $scope.showingAll = false

    $scope.showAll = () ->
        $scope.showingAll = true

    $scope.dayClass = (day) ->
        filtered_day = _.filter($scope.days, { number: parseFloat(day) })
        if (filtered_day.length > 0 and filtered_day[0].isSpecial)
            return " special"

    $scope.badTotal = (day) ->
        total = $scope.getDayTotal(day)
        if (day.isSpecial and total != 0)
            return true
        else if (total != 8 and not day.isSpecial)
            return true
        return false

    $scope.getDayTotal = (day) ->
        total = 0
        for imputation in _.values($scope.imputations)
            total += parseFloat(imputation[day.number])

        holidays = 0
        holidays ?= $scope.holidays[day.number]
        total += holidays
        return total

    $scope.getZebraClass = (projectId) ->
        counter = 0
        for project in _.values($scope.projects)
            if (!$scope.isHidden(project.id) or $scope.showingAll)
                counter++

            if (project.id == projectId and (counter % 2) == 0)
                return "zebra"
            else if (project.id == projectId and (counter % 2) != 0)
                return ""

    $scope.onFocus = (event) ->
        $(event.target).select()

    loadProjects()
@PartCtrl.$inject = ['$scope', '$rootScope', '$http', '$routeParams', '$location', 'apiUrl', 'storage']
