# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import get_url
import requests
import os
import urllib
import json

def sync(doc, method=None):
	"""Sync Webhook under Mandrill account"""
	if not (doc.enable_outgoing
		and doc.service == "Mandrill" and doc.smtp_server
		and doc.email_id and doc.password):
		return

	session = requests.Session()
	if not webhook_exists(doc, session):
		add_webhook(doc, session)

	# always clear key cache
	frappe.cache().delete_value("mandrill_webhook_keys")

def webhook_exists(doc, session):
	"""Use Mandrill API to find a list of existing webhooks"""
	r = session.post(get_api_url("/webhooks/list.json"), data={
		"key": doc.password
	})
	if r.status_code != 200:
		# something went wrong
		frappe.msgprint(_("Could not connect to Mandrill Integration"))
		frappe.errprint(r.text)
		return

	webhooks = r.json()
	return False if len(webhooks)==0 else True

def add_webhook(doc, session):
	"""Use Mandrill API to add the webhook"""
	r = session.post(get_api_url("/webhooks/add.json"), data=json.dumps({
		"key": doc.password,
		"url": get_webhook_post_url(),
		"description": _("Frappé Mandrill Integration"),
		"events": [
			# subscribe to these events
			# NOTE: 'deferral' event wasn't allowed at the time of making this
			"send",
			"hard_bounce",
			"soft_bounce",
			"open",
			"click",
			"spam",
			"unsub",
			"reject"
		]
	}))

	if r.status_code != 200:
		# something went wrong
		frappe.msgprint(_("Could not activate Mandrill Integration"))
		frappe.errprint(r.text)
		return

	# store its value in Email Account
	mandrill_webhook_key = r.json()["auth_key"]
	doc.db_set("mandrill_webhook_key", mandrill_webhook_key)

def get_api_url(api_endpoint):
	"""Get Mandrill API URL for syncing webhooks"""
	return urllib.basejoin('https://mandrillapp.com/api/1.0/', api_endpoint.lstrip("/"))

def get_webhook_post_url():
	"""Get Post URL to be called by Mandrill Webhook"""
	return os.path.join(get_url(), "api", "method", "mandrill_integration.webhook_events.notify")

