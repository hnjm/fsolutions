#  -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
{
  "name"                 :  "POS Invoice Print Without Download",
  "summary"              :  """The module allows you to print invoice without download in POS.""",
  "category"             :  "Point of Sale",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "depends"              :  ['point_of_sale'],
  "data"                 :  [
                             'views/templates.xml',
                             'views/config_view.xml',
                            ],
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=pos_invoice_print_without_download&custom_url=/pos/web", 
  "demo"                 :  [],
  "images"               :  ['static/description/banner.gif'],
  "application"          :  True,
  "installable"          :  True,
  "assets"               :  {
       
        'point_of_sale.assets': [
          "/pos_invoice_print_without_download/static/src/js/main.js",
          "/pos_invoice_print_without_download/static/src/js/model.js",
          "/pos_invoice_print_without_download/static/src/js/print.js",
        
          ],
          'web.assets_qweb': [
            '/pos_invoice_print_without_download/static/src/xml/pos.xml'
            
            
        ],
      },
  "auto_install"         :  False,
  "price"                :  39,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  

  

}