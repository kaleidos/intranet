angular.module('antranet.directives.autofill', []).
    directive('autofill', ($timeout)->
        require: 'ngModel'
        restrict: 'A'
        link: (scope, elem, attrs, ngModel)->
            origVal = elem.val()
            $timeout(->
                newVal = elem.val()
                if(ngModel.$pristine && origVal != newVal)
                    ngModel.$setViewValue(newVal)

            , 1000)
    )
