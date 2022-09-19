#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from calendar import different_locale, month_name, monthrange
from requests import get
from os import system


# https://www.verw.tu-dresden.de/verwricht/formulare/download.asp?file=Arbeitszeitnachweis%20Mindestlohngesetz.pdf
# https://www.verw.tu-dresden.de/formupdate.asp?FileName=Arbeitszeitnachweis gem. Mindestlohngesetz&FileDate=29.03.2021 05:31:10&Subject=D2.4/1 - Stand 18.02.2021 (29.03.2021)
# https://www.verw.tu-dresden.de/verwricht/formulare/download.asp?file=Arbeitszeitnachweis%20Mindestlohngesetz.pdf&sid=C4CB95D3F15A4B34B893AE290001304A
# https://tu-dresden.de/intern/verwaltung/interne_anmeldung
# url_fillpdf = "https://pypi.org/project/fillpdf/"

url_pdf = "https://www.verw.tu-dresden.de/verwricht/formulare/download.asp?file=Arbeitszeitnachweis%20Mindestlohngesetz.pdf"
url_vpn = "https://tu-dresden.de/zih/dienste/service-katalog/arbeitsumgebung/zugang_datennetz/vpn"


data = {
		"Arbeitsbeginn": "08:00",					
		"Geburtsdatum \(dd": {"mm": {"yyyy\)": "26.06.2001"}},
		"Personalnummer": "00267848",
		"Name, Vorname": "Gutmann, Artur",
		"Kostenstelle": "1110407G",
		"Vorgesetzte:r": "Schmutzler, Ludwig",
		"Struktureinheit": "Professur für Computergraphik und Visualisierung",
		"Vertragslaufzeit": "05.22 - 09.22",
		"Vereinbarte Wochenarbeitszeit": "5.5",
	}



def fetch_pdf(url_pdf):
	
	resp = get(url_pdf)

	# in case we are on the other side of the zih-firewall  
	while not "application/pdf" in resp.headers.get("Content-Type"):
	
		print("[!] couldn't fetch pdf, got \"" + resp.headers.get("Content-Type") + "\" instead of \"application/pdf\"")
		print("[!] please either connect with " + print_url(url_vpn, "VPN") +", or go to " + print_url(url_pdf, "verw.tu-dresden.de") + ", login and paste presented link here")
		user = input("[#] (enter for vpn | paste url) > ")
		# if "sid=" in user: cookies = {"TuVerw" : "tuvSID=" + user[user.index("sid=") + 4:]}
		if "sid=" in user: url_pdf = user
		elif user: print("[!] wrong url, please paste the one presented under \"Bitte hier klicken, um die angeforderte Seite abzurufen.\" :)")

		resp = get(url_pdf)

	return resp.content

def get_date() -> datetime:
	date = datetime.now()
	dates = [datetime(date.year + (date.month + i - 1) // 12, (date.month + i - 1) % 12 + 1, 1) for i in range(-5, 5)]
	for i in range(len(dates)):
		print(f"[?] {i}: " + dates[i].strftime("%B %Y"))
	return dates[int(input("[#] (select month) > "))]


def generate_data(data, date):
	
	data["Jahr \(yyyy\)"] = str(date.year)
	with different_locale("de_DE.UTF-8"):
		data["Monat"] = month_name[date.month]

	first_day_of_month, days_in_month = monthrange(date.year, date.month)
	work_hours = float(data["Vereinbarte Wochenarbeitszeit"]) / 5
	work_begin = data.pop("Arbeitsbeginn")
	work_end = f"{int(work_begin[:2]) + work_hours // 1:02.0f}:{int(work_begin[3:]) + (work_hours % 1) * 60:02.0f}"

	for day in range(1, 32):
		invalid = day > days_in_month or (day + first_day_of_month - 1) % 7 in [5, 6]
		data[f"Kommen Tag {day} \(hh:mm\)"] = "-" if invalid else work_begin
		data[f"Gehen Tag {day} \(hh:mm\)"] = "-" if invalid else work_end
		data[f"tatsächliche Stunden Tag {day}"] = "-" if invalid else work_hours
		data[f"Bemerkung Tag {day}"] = "-"

	# there is one imposter among us
	data["Kommen Tag 30"] = data.pop("Kommen Tag 30 \(hh:mm\)")
	data["Gehen Tag 30"] = data.pop("Gehen Tag 30 \(hh:mm\)")

	data["Gesamtstundenzahl"] = f"{sum([value for key, value in data.items() if 'tatsächliche Stunden Tag' in key and value != '-']):02.1f}"
	
	return data


def generate_fdf_rec(data):
	
	fdf = ""
	for key, value in data.items():
		fdf += "<<\n"
		fdf += f"/T ({key})\n"
		if type(value) == dict:
			fdf += "/Kids [\n"
			fdf += generate_fdf_rec(value)
			fdf += "]"
		else:
			fdf += f"/V ({value})\n"
		fdf += ">> \n"
	
	return fdf

def generate_fdf(data):
	
	fdf = ""
	fdf += "%FDF-1.2\n"
	fdf += "%\n"

	fdf += "1 0 obj\n"
	fdf += "\n"
	fdf += "<<\n"
	fdf += "/FDF \n"
	fdf += "<<\n"
	fdf += "/Fields [\n"

	fdf += generate_fdf_rec(data)

	fdf = fdf[:-2]
	fdf += "]\n"
	fdf += ">>\n"
	fdf += ">>\n"
	fdf += "endobj\n"
	fdf += "\n"
	fdf += "trailer\n"
	fdf += "\n"
	fdf += "<<\n"
	fdf += "/Root 1 0 R\n"
	fdf += ">>\n"
	fdf += "%%EOF\n"

	fdf = fdf.encode()
	fdf = fdf.replace(b'\xc3\xbc', b'\xfc')	# ü
	fdf = fdf.replace(b'\xc3\xa4', b'\xe4')	# ä
	fdf = fdf.replace(b'\xc3\xb6', b'\xf6')	# ö

	return fdf


def print_url(url, text):
	return f"\u001b]8;;{url}\u001b\\{text}\u001b]8;;\u001b\\"


if __name__ == "__main__":
	
	# try: from fillpdf import fillpdfs
	# except ModuleNotFoundError: 
		# print("please install " + print_url(url_fillpdf, "fillpdf") + ": \"pip3 install fillpdf\"")
		# exit(-1)

	print("[+] trying to fetch newest pdf from verw.tu-dresden.de...")
	pdf = fetch_pdf(url_pdf)
	print("[+] successfully fetched pdf!")

	date = get_date()

	print("[+] generating fill-data...", end="")
	data = generate_data(data, date)
	print("done!")
	
	print("[+] generating fdf-file...", end="")
	fdf = generate_fdf(data)
	print("done!")

	filename = month_name[date.month].lower() + "_" + data["Name, Vorname"].replace(" ", "_").replace(",", "").lower()

	print("[+] writing \"arbeitszeitnachweis.pdf\" to disk...", end="")
	with open("arbeitszeitnachweis.pdf", "wb") as file:
		file.write(pdf)
	print("done!")
	
	print(f"[+] writing \"{filename}.fdf\" to disk...", end="")
	with open(filename + ".fdf", "wb") as file:
		file.write(fdf)
	print("done!")

	# fillpdfs.write_fillable_pdf("arbeitszeitnachweis.pdf", filename + ".pdf", data)
	# print(f"[+] pdftk arbeitszeitnachweis.pdf fill_form {filename}.fdf output {filename}.pdf")
	print("[+] executing pdftk to fill form-data in pdf...")
	system(f"LD_LIBRARY_PATH=. ./pdftk arbeitszeitnachweis.pdf fill_form {filename}.fdf output {filename}.pdf ")
	print(f"[+] all done :)")