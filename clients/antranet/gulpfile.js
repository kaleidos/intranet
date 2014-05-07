var gulp = require('gulp');
var coffee = require('gulp-coffee');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var connect = require('gulp-connect');
var less = require('gulp-less');
var coffeelint = require('gulp-coffeelint');
var recess = require('gulp-recess');
var jshint = require('gulp-jshint');
var gutil = require('gulp-util');


librariesSources = [
    "app/components/jquery/jquery.js",
    "app/components/jquery-ui/ui/jquery.ui.core.js",
    "app/components/jquery-ui/ui/jquery.ui.widget.js",
    "app/components/jquery-ui/ui/jquery.ui.datepicker.js",
    "app/components/lodash/lodash.js",
    "app/components/underscore.string/lib/underscore.string.js",
    "app/components/backbone/backbone.js",
    "app/components/d3/d3.v2.js",
    "app/lib/lightbox.js",
    "app/components/momentjs/moment.js",
    "app/components/angular/angular.js",
    "app/lib/angular-flash.js",
    "app/components/angular-ui/build/angular-ui.js",
    "app/components/angular-ui/build/angular-ui-ieshiv.js",
    "app/components/angular-sanitize/angular-sanitize.js"
]

applicationSources = [
    'app/coffee/app.coffee',
    'app/coffee/controllers/*.coffee',
    'app/coffee/config.coffee',
    'app/coffee/directives/*.coffee',
    'app/coffee/filters.coffee',
    'app/coffee/services/*.coffee'
]

styleSources = [
    "app/less/base.less",
    "app/less/login.less",
    "app/components/angular-ui/build/angular-ui.css",
    "app/css/jquery-ui/jquery-ui.css"
]

gulp.task('less', function() {
    gulp.src(styleSources)
        .pipe(less().on('error', gutil.log))
        .pipe(concat('antranet.css'))
        .pipe(gulp.dest('app/dist'));
});

gulp.task('pro', ['less'], function() {
    gulp.src(applicationSources)
        .pipe(coffee().on('error', gutil.log))
        .pipe(concat('app.js'))
        .pipe(uglify())
        .pipe(gulp.dest('app/dist/'));
    gulp.src(librariesSources)
        .pipe(concat('libs.js'))
        .pipe(uglify())
        .pipe(gulp.dest('app/dist/'));
});

gulp.task('libs', function() {
    gulp.src(librariesSources)
        .pipe(concat('libs.js'))
        .pipe(gulp.dest('app/dist/'));
});

gulp.task('coffee', function() {
    gulp.src(applicationSources)
        .pipe(coffee().on('error', gutil.log))
        .pipe(concat('app.js'))
        .pipe(gulp.dest('app/dist/'));
});

gulp.task('lint', function() {
    gulp.src(applicationSources)
        .pipe(coffeelint('coffeelint.json'))
        .pipe(coffeelint.reporter())
    gulp.src(['app/less/base.less', 'app/less/login.less'])
        .pipe(recess({strictPropertyOrder: false}))
});


gulp.task('watch', function () {
    gulp.watch(styleSources, ['less']);
    gulp.watch(librariesSources, ['libs']);
    gulp.watch(applicationSources, ['coffee']);
});

gulp.task('connect', connect.server({
    root: ['app'],
    port: 9003,
    livereload: true
}));

gulp.task('default', ['dev', 'watch', 'connect']);

gulp.task('dev', ['coffee', 'less', 'libs']);
