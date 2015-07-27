# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "mandrill_integration"
app_title = "Mandrill Integration"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "Set communication status from Mandrill via webhooks"
app_icon = "octicon octicon-inbox"
app_color = "#4CB6E6"
app_email = "team@frappe.io"
app_version = "0.0.1"

fixtures = ["Custom Field"]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/mandrill_integration/css/mandrill_integration.css"
# app_include_js = "/assets/mandrill_integration/js/mandrill_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/mandrill_integration/css/mandrill_integration.css"
# web_include_js = "/assets/mandrill_integration/js/mandrill_integration.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "mandrill_integration.install.before_install"
# after_install = "mandrill_integration.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mandrill_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

doc_events = {
	"Email Account": {
		"on_update": "mandrill_integration.webhooks.sync"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"mandrill_integration.tasks.all"
# 	],
# 	"daily": [
# 		"mandrill_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"mandrill_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"mandrill_integration.tasks.weekly"
# 	]
# 	"monthly": [
# 		"mandrill_integration.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "mandrill_integration.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "mandrill_integration.event.get_events"
# }

