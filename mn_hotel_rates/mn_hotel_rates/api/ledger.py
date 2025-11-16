# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import hashlib
import json

def create_rate_ledger_entry(doc, method=None):
	"""
	Creates MN Rate Ledger entries for sales documents with hotel items.
	Triggered on submit/update of Quotation, Sales Order, Sales Invoice.
	"""
	if not hasattr(doc, 'items') or not doc.items:
		return

	for idx, item in enumerate(doc.items, start=1):
		# Check if this is a hotel rate item
		mn_service_type = item.get('mn_service_type')
		mn_rate = item.get('mn_rate')

		if not mn_service_type or not mn_rate:
			continue

		# Check if ledger entry already exists for this row
		existing = frappe.db.exists('MN Rate Ledger', {
			'order_doctype': doc.doctype,
			'order_name': doc.name,
			'order_row': idx
		})

		if existing:
			continue

		# Get the rate details for snapshot hash
		rate_doc = frappe.get_doc('MN Rate', mn_rate)
		rate_snapshot = {
			'service_ref': rate_doc.service_ref,
			'room_type_ref': rate_doc.room_type_ref,
			'board': rate_doc.board,
			'net_price': rate_doc.net_price,
			'gross_price': rate_doc.gross_price,
			'uom': rate_doc.uom,
			'per': rate_doc.per
		}
		snapshot_hash = hashlib.md5(json.dumps(rate_snapshot, sort_keys=True).encode()).hexdigest()

		# Create ledger entry
		ledger = frappe.get_doc({
			'doctype': 'MN Rate Ledger',
			'order_doctype': doc.doctype,
			'order_name': doc.name,
			'order_row': idx,
			'mn_rate': mn_rate,
			'unit_price_used': item.rate,
			'quantity': item.qty,
			'total_row_amount': item.amount,
			'snapshot_hash': snapshot_hash,
			'applied_at': frappe.utils.now()
		})
		ledger.insert(ignore_permissions=True)
		frappe.db.commit()
