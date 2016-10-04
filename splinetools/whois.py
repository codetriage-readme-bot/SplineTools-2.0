from splinetools import app
from flask import render_template, flash
from ipwhois import IPWhois, IPDefinedError
from pythonwhois import get_whois
from pythonwhois.shared import WhoisException
from urlparse import urlparse
from geoip import geolite2
import socket, tldextract

WHOIS_ROOT_URL = "/whois"

US_GSA_TLDS = ["gov", "fed"]

#KNOWN_NONSTANDARD_WHOIS_RESPONSES = US_GSA_TLDS - Not needed... yet.

@app.route(WHOIS_ROOT_URL)
def whois_search():
	return render_template("whois_query.html")

@app.route(WHOIS_ROOT_URL+"/ip/<ipaddress>")
def ip_whois(ipaddress):
	try:
		whois_result = IPWhois(ipaddress).lookup()
	except ValueError:
		return render_template("error.html", error="does not appear to be a valid IP address.", error_subject=ipaddress)
	except IPDefinedError as e:
		e_split = str(e).split("'")[2:]
		rfc = e_split[-2].replace("RFC ","rfc").split(",")[0] if "RFC" in e_split[-2] else None
		return render_template("error.html", error="".join(e_split), error_subject=ipaddress, rfc=rfc)
		
	supernet = None
	for net in whois_result['nets']:
		if net['cidr'] == whois_result['asn_cidr']:
			whois_result.update(net)
			supernet = net

	extended_result = (supernet is not None)
	if extended_result:
		whois_result['nets'].remove(supernet)
		
	try:
		rdns_hostname = socket.gethostbyaddr(ipaddress)[0]
	except socket.herror:
		rdns_hostname = None
	
	ip_geo = geolite2.lookup(ipaddress)
	ip_location = ip_geo.location if ip_geo is not None else None
	return render_template("ip.html", ipaddress=ipaddress, rdns_hostname=rdns_hostname, ip_location=ip_location, whois_result=whois_result, extended_result=extended_result)


@app.route(WHOIS_ROOT_URL+"/domain/<hostname>")
def hostname_whois(hostname):
	extracted_domain = tldextract.extract(hostname)
	domain = extracted_domain.registered_domain
	tld = extracted_domain.tld.lower()
	
	if domain == "":
		return render_template("error.html", error=" does not end with a valid TLD.", error_subject=hostname, error_info_url="https://www.icann.org/resources/pages/tlds-2012-02-25-en")
	
	try:
		whois_result = get_whois(domain)
	except WhoisException as e:
		return render_template("error.html", error=" - {}".format(e), error_subject=domain)
		
	if "status" not in whois_result:  # Chances are the domain isn't registered
		return render_template("error.html", error="does not appear to be registered.", error_subject=domain)

	if tld in US_GSA_TLDS:  # whois.dotgov.gov only returns a couple of records; notify the user
		whois_result['registrar'] = ["General Services Administration, United States Federal Government"]
		flash(u"The WHOIS server for .{} is known to return incomplete records.".format(tld), "error")
	
	try:
		ip_list = socket.gethostbyname_ex(domain)[2]
	except socket.gaierror:
		ip_list = []

	return render_template("host.html", hostname=domain, tld=tld, whois_result=whois_result, ip_list=ip_list)