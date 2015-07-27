# Copyright (c) 2015, Frappe Technologies Pvt. Ltd.
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
import hmac
import hashlib
from .webhooks import get_webhook_post_url

@frappe.whitelist(allow_guest=True)
def set_status(mandrill_events=None):
	# print frappe.local.form_dict
	if not authenticate_signature():
		return

	# import json
	# print frappe.as_json(json.loads(mandrill_events), indent=4)


def authenticate_signature():
	"""Returns True if the received signature matches the generated signature"""
	received_signature = frappe.get_request_header("X-Mandrill-Signature")

	# seems like a dummy post request
	if not received_signature:
		return False

	to_hash = get_post_url_for_hashing()
	for key in get_webhook_keys():
		# generate signature using the webhook key
		hashed = hmac.new(key.encode("utf-8"), to_hash, hashlib.sha1)
		generated_signature = hashed.digest().encode("base64").rstrip('\n')

		# matched => authenticated
		if received_signature==generated_signature:
			return True

	# no match => failure
	return False

def get_post_url_for_hashing():
	"""Concats site's post url for set_status, and sorted key and value of request parameters"""
	post_url = get_webhook_post_url()
	post_args = ""

	for key in sorted(frappe.local.form_dict.keys()):
		if key != "cmd":
			post_args += key + frappe.local.form_dict[key]

	return post_url + post_args

def get_webhook_keys():
	"""There could be multiple email accouts with Mandrill Integration"""
	def _get_webhook_keys():
		return [d.mandrill_webhook_key for d in frappe.get_all("Email Account",
			fields=["mandrill_webhook_key"],
			filters={
				"enable_outgoing": 1,
				"service": "Mandrill"
			}) if d.mandrill_webhook_key]

	return frappe.cache().get_value("mandrill_webhook_keys", _get_webhook_keys)
