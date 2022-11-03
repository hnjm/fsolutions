odoo.define("em_pos_multi_uom.TicketScreen", function (require) {
  "use strict";
  const Registries = require("point_of_sale.Registries");
  const TicketScreen = require("point_of_sale.TicketScreen");

  const PosTicketScreen = (TicketScreen) =>
    class extends TicketScreen {
      _getToRefundDetail(orderline) {
        if (orderline.id in this.env.pos.toRefundLines) {
          return this.env.pos.toRefundLines[orderline.id];
        } else {
          const customer = orderline.order.get_client();
          const orderPartnerId = customer ? customer.id : false;
          const newToRefundDetail = {
            qty: 0,
            orderline: {
              id: orderline.id,
              productId: orderline.product.id,
              price: orderline.price,
              qty: orderline.quantity,
              refundedQty: orderline.refunded_qty,
              orderUid: orderline.order.uid,
              orderBackendId: orderline.order.backendId,
              orderPartnerId,
              tax_ids: orderline.get_taxes().map((tax) => tax.id),
              discount: orderline.discount,
              wvproduct_uom: orderline.wvproduct_uom,
            },
            destinationOrderUid: false,
          };
          this.env.pos.toRefundLines[orderline.id] = newToRefundDetail;
          return newToRefundDetail;
        }
      }
      _prepareRefundOrderlineOptions(toRefundDetail) {
        const { qty, orderline } = toRefundDetail;
        return {
          quantity: -qty,
          price: orderline.price,
          extras: { price_manually_set: true },
          merge: false,
          refunded_orderline_id: orderline.id,
          tax_ids: orderline.tax_ids,
          discount: orderline.discount,
          wvproduct_uom: orderline.wvproduct_uom,
        };
      }
    };

  Registries.Component.extend(TicketScreen, PosTicketScreen);
  return TicketScreen;
});
