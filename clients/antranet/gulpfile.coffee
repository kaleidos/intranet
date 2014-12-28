gulp = require('gulp')
coffee = require('gulp-coffee')
concat = require('gulp-concat')
uglify = require('gulp-uglify')
less = require('gulp-less')
coffeelint = require('gulp-coffeelint')
recess = require('gulp-recess')
jshint = require('gulp-jshint')
gutil = require('gulp-util')


librariesSources = [
    "app/components/jquery/dist/jquery.js"
    "app/components/jquery-ui/ui/core.js"
    "app/components/jquery-ui/ui/widget.js"
    "app/components/jquery-ui/ui/datepicker.js"
    "app/components/lodash/dist/lodash.js"
    "app/components/underscore.string/lib/underscore.string.js"
    "app/components/backbone/backbone.js"
    "app/lib/lightbox.js"
    "app/components/d3/d3.v2.js"
    "app/components/momentjs/moment.js"
    "app/components/angular/angular.js"
    "app/lib/angular-flash.js"
    "app/components/angular-ui/build/angular-ui.js"
    "app/components/angular-ui/build/angular-ui-ieshiv.js"
    "app/components/angular-route/angular-route.js"
    "app/components/angular-sanitize/angular-sanitize.js"
]


applicationSources = [
    'app/coffee/app.coffee'
    'app/coffee/classes.coffee'
    'app/coffee/utils.coffee'
    'app/coffee/config.coffee'
    'app/coffee/filters.coffee'
    'app/coffee/services/*.coffee'
    'app/coffee/controllers/*.coffee'
    'app/coffee/directives/*.coffee'
]


styleSources = [
    "app/less/base.less"
    "app/less/login.less"
    "app/components/angular-ui/build/angular-ui.css"
    "app/css/jquery-ui/jquery-ui.css"
    "app/css/font-awesome.css"
]


gulp.task 'less', ->
    gulp.src(styleSources)
        .pipe(less().on('error', gutil.log))
        .pipe(concat('antranet.css'))
        .pipe(gulp.dest('app/dist/styles/'))


gulp.task 'pro', ['less'], ->
    gulp.src(applicationSources)
        .pipe(coffee().on('error', gutil.log))
        .pipe(concat('app.js'))
        #.pipe(uglify())       # FIX ME: Error with the inversion of control
        .pipe(gulp.dest('app/dist/js/'))
    gulp.src(librariesSources)
        .pipe(concat('libs.js'))
        #.pipe(uglify())       # FIX ME: Error with the inversion of control
        .pipe(gulp.dest('app/dist/js/'))


gulp.task 'libs', ->
    gulp.src(librariesSources)
        .pipe(concat('libs.js'))
        .pipe(gulp.dest('app/dist/js/'))


gulp.task 'coffee', ->
    gulp.src(applicationSources)
        .pipe(coffee().on('error', gutil.log))
        .pipe(concat('app.js'))
        .pipe(gulp.dest('app/dist/js/'))

gulp.task 'lint', ->
    gulp.src(applicationSources)
        .pipe(coffeelint('coffeelint.json'))
        .pipe(coffeelint.reporter())
    gulp.src(['app/less/base.less', 'app/less/login.less'])
        .pipe(recess({strictPropertyOrder: false}))


gulp.task 'watch', ->
    gulp.watch(styleSources, ['less'])
    gulp.watch(librariesSources, ['libs'])
    gulp.watch(applicationSources, ['coffee'])


gulp.task "express", ->
    express = require("express")
    app = express()

    app.use("/js", express.static("#{__dirname}/app/dist/js"))
    app.use("/styles", express.static("#{__dirname}/app/dist/styles"))
    app.use("/partials", express.static("#{__dirname}/app/partials"))

    app.all "/*", (req, res, next) ->
        # Just send the index.html for other files to support HTML5Mode
        res.sendFile("index.html", {root: "#{__dirname}/app/"})

    app.listen(9001)


gulp.task 'default', [
    'dev'
    'express'
    'watch'
]

gulp.task 'dev', [
    'coffee'
    'less'
    'libs'
]
