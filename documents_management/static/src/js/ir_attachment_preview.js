odoo.define('documents_management.attachment_preview', function(require) {

    var BasicFields = require('web.basic_fields');
    var DocumentViewer = require('documents_management.IrAttachmentDocumentViewer');

    var core = require('web.core');    
    var qweb = core.qweb;

    BasicFields.FieldBinaryFile.include({
        events: _.extend({}, BasicFields.FieldBinaryFile.prototype.events, {
            'click .o_attachment_preview': "_openDocumentViewer",
        }),

        _renderReadonly: function () {
            var def = this._super.apply(this, arguments);
            if (this.model === 'ir.attachment'){
                var $previewButton = $(qweb.render("attachment_preview_button"));
                this.$el.append($previewButton);
            }
            return def;
        },

        _openDocumentViewer: function(ev) {
            var self = this;
            ev.preventDefault();
            ev.stopPropagation();                       
            var recordData = self.recordData;
            var match = recordData.mimetype.match("(image|video|application/pdf|text)");
            if(match){
                const documents = [{
                    name: recordData.name || recordData.display_name || "",
                    filename: recordData.name || recordData.display_name || "",
                    type: recordData.mimetype || 'application/octet-stream',
                    mimetype: recordData.mimetype || 'application/octet-stream',
                    id: recordData.id,
                    is_main: false,                    
                    url: "/web/content/" + recordData.id + "?download=true",
                }]
                const documentID = recordData.id;
                const documentViewer = new DocumentViewer(self,documents,documentID);
                documentViewer.appendTo($('body'));
            }else{
                alert('This file type is not supported.')
            }
        },
    });
});
