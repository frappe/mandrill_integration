# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd.
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import requests
from .webhooks import get_api_url

def unsubscribe_blacklisted():
	"""Get blacklisted emails, unsubscribe them globally and delete them from Mandrill.
		Run via Daily Scheduler."""
	for email_account in frappe.get_all("Email Account", filters={"service": "Mandrill", "enable_outgoing": 1},
			fields=["password", "mandrill_webhook_key"]):

		# don't do it when mandrill integration is inactive
		if not email_account.mandrill_webhook_key:
			continue

		session = requests.Session()
		blacklisted = get_blacklisted(email_account, session)
		if not blacklisted:
			continue

		remove_from_blacklist(email_account, session, blacklisted)

def get_blacklisted(email_account, session):
	"""Call Mandrill Reject API and get list of blacklisted emails"""
	r = session.post(get_api_url("/rejects/list.json"), data=json.dumps({
		"key": email_account.password
	}))
	if r.status_code != 200:
		handle_blacklist_error()
		return

	blacklisted = r.json()

	return [each_email["email"] for each_email in blacklisted
		if each_email["reason"] in ["hard-bounce", "spam", "unsub"]]

def remove_from_blacklist(email_account, session, blacklist):
	"""Unsubscribe and remove from Mandrill's blacklist"""
	delete_url = get_api_url("/rejects/delete.json")

	for email in blacklist:
		global_unsubscribe_and_commit(email)

		# delete from blacklist
		r = session.post(delete_url, data=json.dumps({
			"key": email_account.password,
			"email": email
		}))

		if r.status_code != 200:
			handle_blacklist_error()
			return

		if not r.json()["deleted"]:
			# didn't get deleted! check logs
			print r.json()

def handle_blacklist_error(r):
	try:
		print r.json()["message"]
	except:
		print r.text

def global_unsubscribe_and_commit(email):
	"""Set Global Unsubscribe for the email and commit"""
	try:
		frappe.get_doc({
			"doctype": "Email Unsubscribe",
			"email": email,
			"global_unsubscribe": 1
		}).insert(ignore_permissions=True)

	except frappe.DuplicateEntryError:
		pass

	else:
		frappe.db.commit()
