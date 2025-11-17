# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
from datetime import datetime, timedelta

@frappe.whitelist()
def search_packages(package_search_name):
	"""
	Execute package search based on MN Package Search criteria.
	Returns cached results from MN Package Quote.

	Args:
		package_search_name: Name of MN Package Search document

	Returns:
		dict: {
			'quote_name': str,
			'price_range_min': float,
			'price_range_max': float,
			'total_packages': int,
			'items': list
		}
	"""
	search = frappe.get_doc("MN Package Search", package_search_name)

	# Check if cached quote exists and is not expired
	cached_quote = get_cached_quote(package_search_name)
	if cached_quote and not cached_quote.is_expired():
		return {
			'quote_name': cached_quote.name,
			'price_range_min': cached_quote.price_range_min,
			'price_range_max': cached_quote.price_range_max,
			'total_packages': cached_quote.total_packages,
			'items': [item.as_dict() for item in cached_quote.items]
		}

	# Execute new search
	# 1. Find hotels in the city/region
	hotels = find_hotels(search.city, search.region_district, search.hotel_category)

	if not hotels:
		frappe.msgprint(_("No hotels found for the specified criteria"))
		return {
			'quote_name': None,
			'price_range_min': 0,
			'price_range_max': 0,
			'total_packages': 0,
			'items': []
		}

	# 2. Calculate packages for each hotel
	packages = []
	for hotel in hotels:
		hotel_packages = calculate_hotel_packages(
			hotel=hotel,
			date_from=search.date_from,
			date_to=search.date_to,
			nights=search.nights,
			adults=search.adults,
			children=search.children,
			board_preference=search.board_preference
		)

		# Add transfer if requested
		if search.include_transfer and search.transfer_type:
			transfer_price = get_transfer_price(
				city=search.city,
				transfer_type=search.transfer_type,
				passengers=search.adults + search.children
			)
		else:
			transfer_price = 0

		# Add to packages
		for pkg in hotel_packages:
			pkg['transfer_included'] = search.include_transfer
			pkg['transfer_price'] = transfer_price
			pkg['total_price_min'] = pkg['hotel_price_min'] + transfer_price
			pkg['total_price_max'] = pkg['hotel_price_max'] + transfer_price
			packages.append(pkg)

	# 3. Create/update Package Quote (cache)
	quote = create_package_quote(search, packages)

	return {
		'quote_name': quote.name,
		'price_range_min': quote.price_range_min,
		'price_range_max': quote.price_range_max,
		'total_packages': quote.total_packages,
		'items': [item.as_dict() for item in quote.items]
	}


def get_cached_quote(package_search_name):
	"""Get cached quote if exists and not expired"""
	quotes = frappe.get_all("MN Package Quote",
		filters={"package_search": package_search_name, "status": "Active"},
		order_by="created_at desc",
		limit=1
	)

	if quotes:
		return frappe.get_doc("MN Package Quote", quotes[0].name)
	return None


def find_hotels(city, region_district=None, category=None):
	"""Find hotels matching location and category criteria"""
	filters = {"status": "Active"}

	if city:
		filters["city"] = city

	if region_district:
		filters["region_district"] = region_district

	if category:
		filters["category"] = category

	hotels = frappe.get_all("Hotel",
		filters=filters,
		fields=["name", "hotel_name", "city", "category", "region_district"]
	)

	return hotels


def calculate_hotel_packages(hotel, date_from, date_to, nights, adults, children, board_preference=None):
	"""
	Calculate available packages for a hotel.
	Returns list of package options with price ranges.
	"""
	packages = []

	# Get room types for this hotel
	room_types = frappe.get_all("Hotel Room Type",
		filters={"hotel": hotel['name'], "status": "Active"},
		fields=["name", "room_type_code", "room_type_name"]
	)

	# Get available boards (or use preference)
	boards = [board_preference] if board_preference else ["BB", "HB", "FB", "AI", "UAI"]

	for room_type in room_types:
		for board in boards:
			# Search for rates
			rate_prices = get_rate_prices(
				hotel=hotel['name'],
				room_type=room_type['name'],
				board=board,
				date_from=date_from,
				date_to=date_to,
				nights=nights,
				adults=adults,
				children=children
			)

			if rate_prices:
				packages.append({
					'hotel': hotel['name'],
					'hotel_category': hotel.get('category'),
					'room_type': room_type['name'],
					'board': board,
					'hotel_price_min': rate_prices['min_price'],
					'hotel_price_max': rate_prices['max_price'],
					'mn_rate_ref': rate_prices.get('rate_name')
				})

	return packages


def get_rate_prices(hotel, room_type, board, date_from, date_to, nights, adults, children):
	"""
	Get price range for hotel rate.
	Calculates total price for the stay.
	"""
	# Search for applicable rates
	rates = frappe.get_all("MN Rate",
		filters={
			"service_type": "hotel",
			"service_ref": hotel,
			"room_type_ref": room_type,
			"board": board,
			"stop_sale": 0,
			"date_from": ["<=", date_from],
			"date_to": [">=", date_to]
		},
		fields=["name", "net_price", "gross_price", "uom", "per", "occupancy_class"],
		order_by="priority desc, net_price asc"
	)

	if not rates:
		return None

	# Calculate total price based on UOM and period
	# Simplified: assuming Per Person Per Day for now
	min_price = None
	max_price = None

	for rate in rates:
		if rate.uom == "Per Person" and rate.per == "Per Day":
			# Price per person per day
			total_pax = adults + children
			price_per_night = rate.net_price * total_pax
			total_price = price_per_night * nights
		elif rate.uom == "Per Room" and rate.per == "Per Day":
			# Price per room per day
			total_price = rate.net_price * nights
		else:
			# Default fallback
			total_price = rate.net_price * nights

		if min_price is None or total_price < min_price:
			min_price = total_price
		if max_price is None or total_price > max_price:
			max_price = total_price

	# Use base rate for calculation
	base_rate = rates[0]

	return {
		'min_price': min_price or 0,
		'max_price': max_price or min_price or 0,
		'rate_name': base_rate.name
	}


def get_transfer_price(city, transfer_type, passengers):
	"""Get transfer price for the city and type"""
	transfers = frappe.get_all("MN Transfer",
		filters={
			"city": city,
			"transfer_type": transfer_type,
			"status": "Active"
		},
		fields=["name", "price_per_transfer", "price_per_person", "max_passengers"],
		order_by="price_per_transfer asc",
		limit=1
	)

	if not transfers:
		return 0

	transfer = transfers[0]

	# Check capacity
	if transfer.max_passengers and passengers > transfer.max_passengers:
		# Need multiple vehicles or larger vehicle
		# For now, return 0 (should implement multi-vehicle logic)
		return 0

	# Calculate price
	if transfer.price_per_transfer:
		return transfer.price_per_transfer
	elif transfer.price_per_person:
		return transfer.price_per_person * passengers
	else:
		return 0


def create_package_quote(search, packages):
	"""Create or update Package Quote with results"""
	# Delete old quotes for this search
	old_quotes = frappe.get_all("MN Package Quote",
		filters={"package_search": search.name}
	)
	for old_quote in old_quotes:
		frappe.delete_doc("MN Package Quote", old_quote.name, ignore_permissions=True)

	# Create new quote
	quote = frappe.get_doc({
		"doctype": "MN Package Quote",
		"package_search": search.name,
		"city": search.city,
		"date_from": search.date_from,
		"date_to": search.date_to,
		"nights": search.nights,
		"adults": search.adults,
		"children": search.children,
		"hotel_category": search.hotel_category,
		"status": "Active"
	})

	# Add items
	for pkg in packages:
		quote.append("items", pkg)

	quote.insert(ignore_permissions=True)
	frappe.db.commit()

	return quote


@frappe.whitelist()
def filter_packages_by_category(quote_name, category):
	"""
	Filter package quote items by hotel category.
	Returns filtered items with updated price range.
	"""
	quote = frappe.get_doc("MN Package Quote", quote_name)

	if quote.is_expired():
		frappe.throw(_("Quote has expired. Please search again."))

	# Filter items
	filtered_items = []
	for item in quote.items:
		if item.hotel_category == category:
			filtered_items.append(item.as_dict())

	# Calculate price range for filtered items
	if filtered_items:
		prices_min = [item['total_price_min'] for item in filtered_items if item.get('total_price_min')]
		prices_max = [item['total_price_max'] for item in filtered_items if item.get('total_price_max')]

		price_range_min = min(prices_min) if prices_min else 0
		price_range_max = max(prices_max) if prices_max else 0
	else:
		price_range_min = 0
		price_range_max = 0

	return {
		'quote_name': quote_name,
		'category': category,
		'price_range_min': price_range_min,
		'price_range_max': price_range_max,
		'total_packages': len(filtered_items),
		'items': filtered_items
	}
