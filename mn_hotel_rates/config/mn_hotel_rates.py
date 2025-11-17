# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Package Search"),
			"items": [
				{
					"type": "doctype",
					"name": "MN Package Search",
					"description": _("Search for hotel packages")
				},
				{
					"type": "doctype",
					"name": "MN Package Quote",
					"description": _("Package search results (cached)")
				},
				{
					"type": "doctype",
					"name": "MN Pre Order",
					"description": _("Pre-orders with release time")
				}
			]
		},
		{
			"label": _("Contracts & Rates"),
			"items": [
				{
					"type": "doctype",
					"name": "MN Contract",
					"description": _("Hotel contract with tariffs and rules")
				},
				{
					"type": "doctype",
					"name": "MN Rate",
					"description": _("Atomic hotel rates (published)")
				},
				{
					"type": "doctype",
					"name": "MN Special Offer",
					"description": _("Special offers and promotions")
				}
			]
		},
		{
			"label": _("Audit & Tracking"),
			"items": [
				{
					"type": "doctype",
					"name": "MN Rate Ledger",
					"description": _("Applied rates audit trail")
				}
			]
		},
		{
			"label": _("Master Data"),
			"items": [
				{
					"type": "doctype",
					"name": "Hotel",
					"description": _("Hotels master")
				},
				{
					"type": "doctype",
					"name": "Hotel Room Type",
					"description": _("Room types catalog")
				},
				{
					"type": "doctype",
					"name": "MN Transfer",
					"description": _("Transfer services")
				}
			]
		}
	]
