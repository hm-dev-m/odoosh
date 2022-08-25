# -*- coding: utf-8 -*-

import odoo
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class PosSumupResponseController(http.Controller):
    
    @http.route('/pos/web/sumup_response', type='http', auth='none')
    def a(self, **query):
        _logger.debug('SumUp transaction RESPONSE: %s' % query)
        # Write SumUp transaction results into Odoo database:
        foreign_tx_id = query.get('foreign-tx-id')
        if foreign_tx_id:
            if query.get('smp-status') == 'success':
                successful = True
                message = ''
            else:
                successful = False
                message = query.get('smp-message')
            smp_tx_code = query.get('smp-tx-code')
            # here can only use the old api
            PosSumupTransaction = request.env['pos.sumup.transaction'].with_context(request.context)
            existed_record_id = PosSumupTransaction.sudo().search(
                [('uuid', '=', foreign_tx_id)], limit=1)
            if existed_record_id:
                PosSumupTransaction.sudo().browse(existed_record_id).write({
                        'successful':   successful,
                        'message':      message,
                        'smp_tx_code':  smp_tx_code,
                    })
            else:
                PosSumupTransaction.sudo().create({
                        'uuid':         foreign_tx_id,
                        'successful':   successful,
                        'message':      message,
                        'smp_tx_code':  smp_tx_code,
                    })
        # Open self close window
        return "<html><body onLoad='window.close();'></html>"
