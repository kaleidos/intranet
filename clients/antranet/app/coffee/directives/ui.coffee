angular.module("antranet.directives.ui", []).
    directive("rating", ($parse, $rootScope)->
        restrict: "AE"
        templateUrl: "partials/tmpl-rating.html"
        scope:
            score: "=score"
            max: "=max"
            rating: "=rating"
        link: (scope, elements, attrs) ->
            scope.updateStars = () ->
                scope.stars = []
                for idx in [0...scope.max]
                    scope.stars.push({full: scope.score > idx})

            scope.starClass = (star, idx) ->
                return if star.full then "fa-star" else "fa-star-o"

            scope.starColor = (idx) ->
                return if idx <= scope.hoverIdx then "rating-highlight" else "rating-normal"

            scope.showHover = (idx) ->
                scope.hoverIdx = idx

            scope.hideHover = () ->
                scope.hoverIdx = -1

            scope.setRating = (idx) ->
                scope.score = idx + 1
                scope.$emit 'update-rate', scope.rating, scope.score

            scope.$watch "score", (newVal, oldVal) ->
                if newVal != null && newVal != undefined
                    scope.updateStars()
    )

