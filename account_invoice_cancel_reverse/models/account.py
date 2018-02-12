from datetime import date
from datetime import datetime
# from datetime import timedelta
# from dateutil import relativedelta
# import time

from odoo import models, fields, api, _
from openerp.exceptions import UserError
# from openerp.tools.safe_eval import safe_eval as eval
# from openerp.tools.translate import _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def action_cancel(self):
        moves = self.env['account.move']
        move_obj = self.env['account.move']
        for inv in self:
            if inv.move_id:
                moves += inv.move_id
            if inv.payment_move_line_ids:
                raise UserError(_('You cannot cancel an invoice which is partially paid. You need to unreconcile related payment entries first.'))

        # First, set the invoices as cancelled and detach the move ids
        self.write({'state': 'cancel'})
        if moves:
            for move in moves:
                rev_move_id = moves.reverse_moves()[0]
                rev_move_line = move_obj.browse(rev_move_id).line_ids.filtered('account_id.reconcile')
                move_line = move.line_ids.filtered('account_id.reconcile')
                (rev_move_line + move_line).reconcile()
        return True