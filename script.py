#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from calendar import different_locale, month_name, monthrange
from subprocess import run
from sys import argv
import json
from os import remove


# https://www.verw.tu-dresden.de/verwricht/formulare/download.asp?file=Arbeitszeitnachweis%20Mindestlohngesetz.pdf
# https://www.verw.tu-dresden.de/formupdate.asp?FileName=Arbeitszeitnachweis gem. Mindestlohngesetz&FileDate=29.03.2021 05:31:10&Subject=D2.4/1 - Stand 18.02.2021 (29.03.2021)
# https://www.verw.tu-dresden.de/verwricht/formulare/download.asp?file=Arbeitszeitnachweis%20Mindestlohngesetz.pdf&sid=C4CB95D3F15A4B34B893AE290001304A
# https://tu-dresden.de/intern/verwaltung/interne_anmeldung
# url_fillpdf = "https://pypi.org/project/fillpdf/"


data = {
		"Arbeitsbeginn": "08:00",					
		"Geburtsdatum \(dd": {"mm": {"yyyy\)": "01.01.0101"}},
		"Personalnummer": "12345678",
		"Name, Vorname": "Mustermann, Max",
		"Kostenstelle": "1234567A",
		"Vorgesetzte:r": "Mustermann, Moritz",
		"Struktureinheit": "Professur für Staatsgeheimnisse",
		"Vertragslaufzeit": "01.01 - 02.02",
		"Vereinbarte Wochenarbeitszeit": "5.5",
	}


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
		weekday = (day + first_day_of_month - 1) % 7
		invalid = day > days_in_month or weekday in [5, 6]
		if invalid:
			begin = "-"
			end = "-"
			hours = "-"
		elif jsoncall:
			hours = float(worktime[weekday]["arbeitszeit"])
			if hours == 0:
				hours = begin = end = "-"
			else:
				begin = worktime[weekday]["startzeit"]
				end = worktime[weekday]["endzeit"]
		else:
			begin = work_begin
			end = work_end
			hours = work_hours
		data[f"Kommen Tag {day} \(hh:mm\)"] = begin
		data[f"Gehen Tag {day} \(hh:mm\)"] = end
		data[f"tatsächliche Stunden Tag {day}"] = hours
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


if __name__ == "__main__":
	jsoncall = False

	if len(argv) >= 2:
		jsoncall = True
		verbose = True if len(argv) >= 3 and (argv[2] == "--verbose" or argv[2] == "-v") else False
		if verbose:
			print("[+] Using provided JSON data!")

		jsonobj = json.loads(argv[1])
		personal = jsonobj["personal"]
		worktime = jsonobj["worktime"]
		mon = jsonobj["month"]
		data["Geburtsdatum \(dd"] = personal["Geburtsdatum \(dd"]
		data["Personalnummer"] = personal["Personalnummer"]
		data["Name, Vorname"] = personal["Name, Vorname"]
		data["Kostenstelle"] = personal["Kostenstelle"]
		data["Vorgesetzte:r"] = personal["Vorgesetzte:r"]
		data["Struktureinheit"] = personal["Struktureinheit"]
		data["Vertragslaufzeit"] = personal["Vertragslaufzeit"]
		data["Vereinbarte Wochenarbeitszeit"] = personal["Vereinbarte Wochenarbeitszeit"]

	date = datetime(year=int(mon["year"]), month=int(mon["month"]), day=1) if jsoncall else get_date()


	if verbose:
		print("[+] generating fill-data...", end="")
	data = generate_data(data, date)
	if verbose:
		print("done!")

	if verbose:
		print("[+] generating fdf-file...", end="")
	fdf = generate_fdf(data)
	if verbose:
		print("done!")

	filename = month_name[date.month].lower() + "_" + data["Name, Vorname"].replace(" ", "_").replace(",", "").lower()

	if verbose:
		print(f"[+] writing \"{filename}.fdf\" to disk...", end="")
	with open(filename + ".fdf", "wb") as file:
		file.write(fdf)
	if verbose:
		print("done!")

	# fillpdfs.write_fillable_pdf("arbeitszeitnachweis.pdf", filename + ".pdf", data)
	# print(f"[+] pdftk arbeitszeitnachweis.pdf fill_form {filename}.fdf output {filename}.pdf")
	if verbose:
		print("[+] executing qpdf and pdftk to generate filled pdf...", end="")
	run(["pdftk", "arbeitszeitnachweis.pdf" ,"fill_form" , filename + ".fdf", "output", filename + ".pdf"], check = True, env = {"PATH": "./", "LD_LIBRARY_PATH": "./"})
	if verbose:
		print("done!")

	if verbose:
		print(f"[+] removing \"{filename}.fdf\"...", end="")
	remove(filename + ".fdf")
	if verbose:
		print("done!")

	if not verbose:
		print(filename)

	if verbose:
		print(f"[+] all done :)")