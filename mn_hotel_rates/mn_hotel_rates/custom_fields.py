# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_sales_document_custom_fields():
	"""
	Create custom fields in Quotation Item, Sales Order Item, and Sales Invoice Item
	to support MN Hotel Rates integration.
	"""

	custom_fields = {
		"Quotation Item": [
			{
				"fieldname": "mn_service_type",
				"label": "MN Service Type",
				"fieldtype": "Select",
				"options": "hotel\ntransfer\nexcursion",
				"insert_after": "item_code"
			},
			{
				"fieldname": "mn_service_ref",
				"label": "MN Service",
				"fieldtype": "Dynamic Link",
				"options": "mn_service_type",
				"insert_after": "mn_service_type"
			},
			{
				"fieldname": "mn_rate",
				"label": "MN Rate",
				"fieldtype": "Link",
				"options": "MN Rate",
				"insert_after": "mn_service_ref"
			},
			{
				"fieldname": "mn_room_type",
				"label": "MN Room Type",
				"fieldtype": "Link",
				"options": "Hotel Room Type",
				"insert_after": "mn_rate"
			},
			{
				"fieldname": "mn_board",
				"label": "MN Board",
				"fieldtype": "Select",
				"options": "RO\nBB\nHB\nFB\nAI\nUAI",
				"insert_after": "mn_room_type"
			},
			{
				"fieldname": "mn_column_break",
				"fieldtype": "Column Break",
				"insert_after": "mn_board"
			},
			{
				"fieldname": "mn_date_from",
				"label": "MN Date From",
				"fieldtype": "Date",
				"insert_after": "mn_column_break"
			},
			{
				"fieldname": "mn_date_to",
				"label": "MN Date To",
				"fieldtype": "Date",
				"insert_after": "mn_date_from"
			},
			{
				"fieldname": "mn_nights",
				"label": "MN Nights",
				"fieldtype": "Int",
				"insert_after": "mn_date_to"
			},
			{
				"fieldname": "mn_pax",
				"label": "MN Pax",
				"fieldtype": "Int",
				"insert_after": "mn_nights"
			},
			{
				"fieldname": "mn_is_supplement",
				"label": "MN Is Supplement",
				"fieldtype": "Check",
				"insert_after": "mn_pax"
			}
		],
		"Sales Order Item": [
			{
				"fieldname": "mn_service_type",
				"label": "MN Service Type",
				"fieldtype": "Select",
				"options": "hotel\ntransfer\nexcursion",
				"insert_after": "item_code"
			},
			{
				"fieldname": "mn_service_ref",
				"label": "MN Service",
				"fieldtype": "Dynamic Link",
				"options": "mn_service_type",
				"insert_after": "mn_service_type"
			},
			{
				"fieldname": "mn_rate",
				"label": "MN Rate",
				"fieldtype": "Link",
				"options": "MN Rate",
				"insert_after": "mn_service_ref"
			},
			{
				"fieldname": "mn_room_type",
				"label": "MN Room Type",
				"fieldtype": "Link",
				"options": "Hotel Room Type",
				"insert_after": "mn_rate"
			},
			{
				"fieldname": "mn_board",
				"label": "MN Board",
				"fieldtype": "Select",
				"options": "RO\nBB\nHB\nFB\nAI\nUAI",
				"insert_after": "mn_room_type"
			},
			{
				"fieldname": "mn_column_break",
				"fieldtype": "Column Break",
				"insert_after": "mn_board"
			},
			{
				"fieldname": "mn_date_from",
				"label": "MN Date From",
				"fieldtype": "Date",
				"insert_after": "mn_column_break"
			},
			{
				"fieldname": "mn_date_to",
				"label": "MN Date To",
				"fieldtype": "Date",
				"insert_after": "mn_date_from"
			},
			{
				"fieldname": "mn_nights",
				"label": "MN Nights",
				"fieldtype": "Int",
				"insert_after": "mn_date_to"
			},
			{
				"fieldname": "mn_pax",
				"label": "MN Pax",
				"fieldtype": "Int",
				"insert_after": "mn_nights"
			},
			{
				"fieldname": "mn_is_supplement",
				"label": "MN Is Supplement",
				"fieldtype": "Check",
				"insert_after": "mn_pax"
			}
		],
		"Sales Invoice Item": [
			{
				"fieldname": "mn_service_type",
				"label": "MN Service Type",
				"fieldtype": "Select",
				"options": "hotel\ntransfer\nexcursion",
				"insert_after": "item_code"
			},
			{
				"fieldname": "mn_service_ref",
				"label": "MN Service",
				"fieldtype": "Dynamic Link",
				"options": "mn_service_type",
				"insert_after": "mn_service_type"
			},
			{
				"fieldname": "mn_rate",
				"label": "MN Rate",
				"fieldtype": "Link",
				"options": "MN Rate",
				"insert_after": "mn_service_ref"
			},
			{
				"fieldname": "mn_room_type",
				"label": "MN Room Type",
				"fieldtype": "Link",
				"options": "Hotel Room Type",
				"insert_after": "mn_rate"
			},
			{
				"fieldname": "mn_board",
				"label": "MN Board",
				"fieldtype": "Select",
				"options": "RO\nBB\nHB\nFB\nAI\nUAI",
				"insert_after": "mn_room_type"
			},
			{
				"fieldname": "mn_column_break",
				"fieldtype": "Column Break",
				"insert_after": "mn_board"
			},
			{
				"fieldname": "mn_date_from",
				"label": "MN Date From",
				"fieldtype": "Date",
				"insert_after": "mn_column_break"
			},
			{
				"fieldname": "mn_date_to",
				"label": "MN Date To",
				"fieldtype": "Date",
				"insert_after": "mn_date_from"
			},
			{
				"fieldname": "mn_nights",
				"label": "MN Nights",
				"fieldtype": "Int",
				"insert_after": "mn_date_to"
			},
			{
				"fieldname": "mn_pax",
				"label": "MN Pax",
				"fieldtype": "Int",
				"insert_after": "mn_nights"
			},
			{
				"fieldname": "mn_is_supplement",
				"label": "MN Is Supplement",
				"fieldtype": "Check",
				"insert_after": "mn_pax"
			}
		]
	}

	create_custom_fields(custom_fields, update=True)


def execute():
	"""Execute during migration or setup"""
	create_sales_document_custom_fields()
