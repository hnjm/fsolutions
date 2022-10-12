odoo.define("print_report_preview.report_preview_dialog", function (require) {
    "use strict";

    var Widget = require("web.Widget");
    var core = require('web.core');
    
    var _t = core._t;
    var _lt = core._lt;

    var ReportPreviewDialog = Widget.extend({
        template: "ReportPreviewDialog",
        events: {
            'click .preview-maximize': '_onMaximize',
            'click .preview-minimize': '_onMinimize',
            'click .preview-destroy':  '_onDestroy',
        },
        init: function(parent, url, title) {
            this._super.apply(this, arguments);            
            this.url = url;
            this.title = title || _t("Preview");             
        },
        renderElement: function() {
            this._super();
            var self = this;
            self.$iframe = self.$el.find(".modal-body .o_preview_pdf_iframe");
            var def = new $.Deferred();
            var viewerURL = "/web/static/lib/pdfjs/web/viewer.html?file=";
            viewerURL += encodeURIComponent(this.url).replace(/'/g,"%27").replace(/"/g,"%22") + "#page=1&zoom=100";
            def.resolve(self.$iframe.attr('src', viewerURL));
            return $.when(def);
        },
        _onOpen: function(){
            this.open();
        },
        open: function() {
            var self = this;
            self.renderElement().then(function(){
                self.$el.modal("show");
            })
            return self;
        },
        _onDestroy: function () {      
            this.destroy();
        },
        destroy: function () {
            if (this.isDestroyed()) {
                return;
            }
            this.$el.modal('hide');
            this.$el.remove();
            this._super.apply(this, arguments);
        },
        _onMaximize: function(){
            this.$el.find(".preview-minimize").toggle();
            this.$el.find(".preview-maximize").toggle();
            this.$el.find(".modal-dialog").addClass("modal-full");
        },
        _onMinimize: function(){
            this.$el.find(".preview-maximize").toggle();
            this.$el.find(".preview-minimize").toggle();
            this.$el.find(".modal-dialog").removeClass("modal-full");
        }
    });
    return ReportPreviewDialog;
});