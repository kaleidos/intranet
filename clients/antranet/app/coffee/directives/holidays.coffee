angular.module('antranet.directives.holidays', []).
    directive('holidaysChart', ->
        link: (scope, elm, attrs) ->
            element = angular.element(elm)

            update = () ->
                element.empty()
                svg = d3.select(element[0]).append("svg").attr("width", 440).attr("height", 260)

                counter = 0
                years = _.map scope.years, (item) ->
                    counter += 15
                    return {
                        year: item.year
                        id: item.id
                        y: counter
                        selected: scope.year.id == item.id
                    }

                data = [
                    {
                        'value': (scope.year.total_days - scope.year.requested_days - scope.year.consumed_days)
                        'color': '#a2bf2f'
                        'cy': 15
                        'legend': (scope.year.total_days - scope.year.requested_days - scope.year.consumed_days)+' Available days'
                    }
                    {
                        'value': scope.year.consumed_days
                        'color': '#42a2bf'
                        'cy': 30
                        'legend': scope.year.consumed_days+' Consumed days'
                    }
                    {
                        'value': scope.year.requested_days
                        'color': '#bf422f'
                        'cy': 45
                        'legend': scope.year.requested_days+' Requested days'
                    }
                ]

                pie = d3.layout.pie()
                    .value((d) -> return d.value)
                    .startAngle(-Math.PI/2)
                    .endAngle(Math.PI/2)

                gs = [
                    { 'func': 'translate(230, 250)', id: 'g0' }
                    { 'func': 'translate(20,10)', id: 'g1' }
                    { 'func': 'translate(370, 20)', id: 'g2' }
                ]

                g = svg.selectAll('g')
                    .data(gs)
                    .enter()
                    .append('g')
                    .attr('transform', (d) -> return d.func )
                    .attr('id', (d) -> return d.id )

                svg.select('g#g0').selectAll("path")
                    .data(pie(data))
                    .enter()
                    .append('svg:path')
                    .attr('stroke', 'grey')
                    .attr('fill', (d) -> return d.data.color )
                    .attr("d", d3.svg.arc().innerRadius(50).outerRadius(160))

                svg.select('g#g1').selectAll("circle")
                    .data(data)
                    .enter()
                    .append('circle')
                    .attr('fill', (d) -> return d.color)
                    .attr('cy', (d) -> return d.cy)
                    .attr('r', 5)
                    .attr('cx', -10)
                    .attr('stroke', 'grey')

                svg.select('g#g1').selectAll("text")
                    .data(data)
                    .enter()
                    .append('text')
                    .attr('x', 0)
                    .attr('y', (d) -> return d.cy+5)
                    .text((d) -> return d.legend)

                svg.select('g#g2').selectAll("text")
                    .data(years)
                    .enter()
                    .append('text')
                    .attr('class', (d) ->
                        if(d.selected)
                            return "year-menu selected"
                        else
                            return "year-menu"
                    )
                    .attr('rel', (d) -> return d.id)
                    .attr('x', 0)
                    .attr('y', (d) -> return d.y)
                    .text((d) -> return d.year)

                element.on('click', 'svg g#g2 text', (event) ->
                    target = angular.element(event.currentTarget)
                    scope.$apply(->
                        scope.setHolidayYearById(parseInt(target.attr('rel'), 10))
                    )
                )

            scope.$on 'holidaysReload', (event) ->
                update()
    ).directive('holidaysCalendar', ->
        link: (scope, elm, attrs) ->
            element = angular.element(elm)

            update = (year) ->
                weekday=["Su", "Mo","Tu","We","Th","Fr","Sa"]
                months=[
                    [0, "January"]
                    [1, "February"]
                    [2, "March"]
                    [3, "April"]
                    [4, "May"]
                    [5, "June"]
                    [6, "July"]
                    [7, "August"]
                    [8, "September"]
                    [9, "October"]
                    [10, "November"]
                    [11, "December"]
                ]
                month = {}
                table = ''
                yearSpecialDays = _.map(year.special_days, (specialDay) -> [moment(specialDay.date, "YYYY-MM-DD"), specialDay.description])
                for monthTuple in months
                    if monthTuple[0] <= 8
                        start = moment("#{year.year}-0#{monthTuple[0] + 1}-01", "YYYY-MM-DD")
                        end = moment("#{year.year}-0#{monthTuple[0] + 1}-01", "YYYY-MM-DD")
                    else
                        start = moment("#{year.year}-#{monthTuple[0] + 1}-01", "YYYY-MM-DD")
                        end = moment("#{year.year}-#{monthTuple[0] + 1}-01", "YYYY-MM-DD")
                    end.add('months', 1)

                    monthSpecialDays = _.filter(yearSpecialDays, (specialDay) -> specialDay[0].month() == monthTuple[0])

                    row1 = "<tr><th colspan='31'>#{monthTuple[1]}</th>"
                    row2 = "<tr>"
                    row3 = "<tr>"

                    while start < end
                        specialTitle = ""
                        if start.day() == 0 or start.day() == 6
                            specialDayClass = "special-day"
                        else
                            specialDayClass = ""

                        isSpecialDay = _.indexOf(_.map(monthSpecialDays, (day) -> return day[0].date()), start.date())
                        if isSpecialDay != -1
                            specialDayClass = "special-day"
                            specialTitle = monthSpecialDays[isSpecialDay][1]

                        row2 += "<td class='week-day #{specialDayClass}' title='#{specialTitle}'>" + weekday[start.day()] + '</td>'

                        tdClass = ''
                        if scope.holidays_requests?
                            for holiday_request in scope.holidays_requests
                                hBegin = moment(holiday_request.beginning, "YYYY-MM-DD")
                                hEnd = moment(holiday_request.ending, "YYYY-MM-DD")
                                if hBegin <= start <= hEnd
                                    tdClass=scope.getStatusName(holiday_request.status)

                        row3 += "<td class='#{tdClass} #{specialDayClass}' title='#{specialTitle}'>" + start.date() + "</td>"
                        month[months[start.month()][1]] = if month[months[start.month()][1]]? then 1 else month[months[start.month()][1]] + 1

                        start.add('days', 1)

                    row1 += "</tr>"
                    row2 += "</tr>"
                    row3 += "</tr>"
                    table += "<table>" + row1+row2+row3 + "</table>"
                element.html(table)

            scope.$on 'holidaysReload', (event) ->
                update(scope.year)
        )
