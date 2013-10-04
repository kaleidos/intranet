(function() {
    tinymce.create('tinymce.plugins.InplaceEdit', {
        init : function(ed, url) {
            var t = this

            t.id = ed.id + '-inplace-edit';

            if (ed.settings.inplace_edit) {

                var saveInline = function(ed, ev, ob) {
                    if (ed.isDirty()) {
                        ed.save();
                    }
                };
                ed.onEvent.add(saveInline);
                ed.onChange.add(saveInline);
            }
        },
        getInfo: function() {
            return {
                longname : 'Inplace Edit plugin',
                author : 'Yaco',
                authorurl : 'http://www.yaco.es',
                infourl : 'http://www.yaco.es',
                version : tinymce.majorVersion + "." + tinymce.minorVersion
            };
            }
    });

    tinymce.PluginManager.add('inplaceedit', tinymce.plugins.InplaceEdit);
})();
