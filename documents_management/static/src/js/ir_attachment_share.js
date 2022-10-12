odoo.define('documents_management.attachment_share', function(require) {
    "use strict";

    var FormRenderer = require('web.FormRenderer');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;
    
    FormRenderer.include({                
        _renderView: function() {
            var self = this;
            var def = this._super.apply(this, arguments);
            def.then(function() {
            if(self.mode === 'readonly') {
                self._renderShareButton();
            }
            });
            return def;
        },

        _renderShareButton: function() {
            if (this.state.model === 'ir.attachment'){
                var $sharebutton = $('<div>');
                $sharebutton.addClass("attachment_share_button");
                $sharebutton.append($('<button>').addClass("btn btn-primary").append($('<i class="fa fa-share-alt"/>')));
                $sharebutton.on('click', _.bind(this._clickShareButton, this));
                this.$el.find('.o_form_sheet').append($sharebutton);
            }            
        },

        _clickShareButton: function(ev) {
            ev.stopPropagation();
            ev.preventDefault();            
            var self = this;                
            var action = {
                name: _t('Share Attachments'),
                type: 'ir.actions.act_window',
                res_model: 'ir.attachment.share',                
                view_mode: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    active_model : self.state.model || false,
                    default_res_id : self.state.res_id || false,
                    active_id : self.state.res_id || false,
                },
            };
            return this.do_action(action);
        },


    });
    
});