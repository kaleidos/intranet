module.exports = (grunt) ->
    librariesSources = [
        "app/components/jquery/jquery.js"
        "app/components/jquery-ui/ui/jquery.ui.core.js"
        "app/components/jquery-ui/ui/jquery.ui.widget.js"
        "app/components/jquery-ui/ui/jquery.ui.datepicker.js"
        "app/components/lodash/lodash.js"
        "app/components/underscore.string/lib/underscore.string.js"
        "app/components/backbone/backbone.js"
        "app/components/d3/d3.v2.js"
        "app/lib/lightbox.js"
        "app/components/momentjs/moment.js"
        "app/components/angular/angular.js"
        "app/lib/angular-flash.js"
        "app/components/angular-ui/build/angular-ui.js"
        "app/components/angular-ui/build/angular-ui-ieshiv.js"
    ]

    applicationSources = [
        'app/coffee/app.coffee'
        'app/coffee/controllers/*.coffee'
        'app/coffee/config.coffee'
        'app/coffee/directives/*.coffee'
        'app/coffee/filters.coffee'
        'app/coffee/services/*.coffee'
    ]

    # Project configuration.
    grunt.initConfig
        pkg: grunt.file.readJSON('package.json')

        less:
            app:
                options:
                    paths: ["app/less/"]
                    yuicompress: true
                files:
                    "app/dist/antranet.css": [
                        "app/less/base.less"
                        "app/less/login.less"
                        "app/css/angular-ui.css"
                        "app/css/jquery-ui/jquery-ui.css"
                    ]

        uglify:
            options:
                banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
                mangle: false
                report: 'min'

            libs:
                dest: "app/dist/libs.js"
                src: librariesSources

            app:
                dest: "app/dist/app.js"
                src: "app/dist/_app.js"

        coffee:
            app:
                options:
                    join: false
                files:
                    "app/dist/app.js": applicationSources
            appDist:
                options:
                    join: false
                files:
                    "app/dist/_app.js": applicationSources

        coffeelint:
            app: applicationSources

        concat:
            options:
                separator: ';'
                banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
                        '<%= grunt.template.today("yyyy-mm-dd") %> */\n'

            libs:
                dest: "app/dist/libs.js"
                src: librariesSources
        copy: {
            libs: {
                files: [
                    {expand: true, flatten: true, src: ['app/css/jquery-ui/images/**'], dest: 'app/dist/images'}
                ]
            }
        }

        watch:
            less:
                files: ['app/less/**/*.less']
                tasks: ['less:app']

            coffeeApp:
                files: 'app/coffee/**/*.coffee'
                tasks: ['coffee:app']

            libs:
                files: 'app/libs/*.js'
                tasks: 'concat:libs'

        connect:
            devserver:
                options:
                    port: 9003,
                    base: 'app'

    # Load the plugin that provides the "uglify" task.
    grunt.loadNpmTasks('grunt-contrib-uglify')
    grunt.loadNpmTasks('grunt-contrib-concat')
    grunt.loadNpmTasks('grunt-contrib-less')
    grunt.loadNpmTasks('grunt-contrib-watch')
    grunt.loadNpmTasks('grunt-contrib-connect')
    grunt.loadNpmTasks('grunt-contrib-jshint')
    grunt.loadNpmTasks('grunt-contrib-htmlmin')
    grunt.loadNpmTasks('grunt-contrib-coffee')
    grunt.loadNpmTasks('grunt-contrib-copy')
    grunt.loadNpmTasks('grunt-coffeelint')

    grunt.registerTask('dev', [
        'concat:libs'
        'copy:libs'
        'coffee:app'
        'less:app'
    ])

    grunt.registerTask("pro", [
        'coffee:appDist'
        'uglify:libs'
        'uglify:app'
        'less:app'
        'copy:libs'
    ])

    grunt.registerTask('default', [
        'dev'
        'connect'
        'watch'
    ])
