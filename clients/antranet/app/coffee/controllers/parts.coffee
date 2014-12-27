module = angular.module("antranet.controllers.parts", [])


PartsCtrl = ($scope, $rootScope, rs) ->
    $scope.currentPage = 1

    $rootScope.selectedMenu = "parts"

    loadParts = () ->
        params = {
            page: $scope.currentPage
            page_size: 15
        }

        success = (data) ->
            $scope.parts = data.models
            $scope.hasNext = data.next != null
            $scope.hasPrev = data.previous != null
            $scope.pages = [1.. ((data.count / 15) + 1)]

        rs.listPaginatedParts(params).then(success)

    $scope.sendPart = (part) ->
        rs.setPartSend(part.id).then (data) ->
            loadParts()

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

PartsCtrl.$inject = ['$scope', '$rootScope', 'resource']


PartCtrl = ($scope, $rootScope, $routeParams, $location, rs, storage) ->
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
            days.push({
                number: day.date()
                week: week_days[day.day()]
                isSpecial: isSpecial
            })
            day.add('days', 1)
        return days

    loadPart = (partId) ->
        success = (data) ->
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

        rs.getPart(partId).then(success)

    loadProjects = () ->
        success = (data) ->
            $scope.projects = {}
            for project in data
                $scope.projects[project.id] = project
            loadPart($routeParams.id)

        rs.listProjects().then(success)

    loadHolidays = () ->
        params = {
            year: $scope.part.year
            month: $scope.part.month
        }

        success = (data) ->
            $scope.holidays = {}
            for day in $scope.days
                $scope.holidays[day.number] = 0
            for date in data
                $scope.holidays[date.day] = 8
                $scope.days[date.day-1].isSpecial = true

        rs.listHolidays(params).then(success)

    $scope.savePart = () ->
        if $scope.part.state == 10
            return null

        $scope.part.setAttr("data", $scope.imputations)

        $scope.part.save().then (data) ->
            $location.url('/parts')

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

PartCtrl.$inject = ['$scope', '$rootScope', '$routeParams', '$location', 'resource', 'storage']


module.controller("PartsCtrl", PartsCtrl)
module.controller("PartCtrl", PartCtrl)
