# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

def after_install():
	"""Called after app installation"""
	try:
		# Create custom fields
		from mn_hotel_rates.mn_hotel_rates.custom_fields import create_sales_document_custom_fields
		create_sales_document_custom_fields()
		frappe.msgprint(_("MN Hotel Rates custom fields created successfully"))
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "MN Hotel Rates Installation Error")
		frappe.throw(_("Error during installation: {0}").format(str(e)))
