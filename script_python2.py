#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from calendar import month_name, monthrange
import locale
locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
from subprocess import call
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


def generate_data(data, date):
	data["Jahr \(yyyy\)"] = str(date.year)
	data["Monat"] = month_name[date.month]

	first_day_of_month, days_in_month = monthrange(date.year, date.month)

	for day in range(1, 32):
		weekday = (day + first_day_of_month - 1) % 7
		invalid = day > days_in_month or weekday in [5, 6]
		if invalid:
			begin = "-"
			end = "-"
			hours = "-"
		else:
			hours = float(worktime[weekday]["arbeitszeit"])
			if hours == 0:
				hours = begin = end = "-"
			else:
				begin = worktime[weekday]["startzeit"]
				end = worktime[weekday]["endzeit"]

		data["Kommen Tag " + str(day) + " \(hh:mm\)"] = begin
		data["Gehen Tag " + str(day) + " \(hh:mm\)"] = end
		data["tatsächliche Stunden Tag " + str(day)] = hours
		data["Bemerkung Tag " + str(day)] = "-"

	# there is one imposter among us
	data["Kommen Tag 30"] = data.pop("Kommen Tag 30 \(hh:mm\)")
	data["Gehen Tag 30"] = data.pop("Gehen Tag 30 \(hh:mm\)")

	gesamtStundenZahl = sum([value for key, value in data.items() if 'tatsächliche Stunden Tag' in key and value != '-'])
	data["Gesamtstundenzahl"] = str(round(gesamtStundenZahl * 10) / 10.0)

	return data


def generate_fdf_rec(data):
	fdf = ""
	for key, value in data.items():
		fdf += "<<\n"
		fdf += "/T (" + str(key) + ")\n"
		if type(value) == dict:
			fdf += "/Kids [\n"
			fdf += generate_fdf_rec(value)
			fdf += "]"
		else:
			fdf += "/V (" + str(value) + ")\n"
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

	fdf = fdf.decode(encoding="UTF-8")
	fdf = fdf.encode(encoding="UTF-8")
	fdf = fdf.replace(b'\xc3\xbc', b'\xfc')	# ü
	fdf = fdf.replace(b'\xc3\xa4', b'\xe4')	# ä
	fdf = fdf.replace(b'\xc3\xb6', b'\xf6')	# ö

	return fdf


if __name__ == "__main__":

	if len(argv) < 2:
		raise ValueError("1 argument expected, 0 given")

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

	date = datetime(year=int(mon["year"]), month=int(mon["month"]), day=1)

	data = generate_data(data, date)

	fdf = generate_fdf(data)

	filename = month_name[date.month].lower() + "_" + data["Name, Vorname"].replace(" ", "_").replace(",", "").lower()

	with open(filename + ".fdf", "wb") as file:
		file.write(fdf)

	# fillpdfs.write_fillable_pdf("arbeitszeitnachweis.pdf", filename + ".pdf", data)
	# print(f"[+] pdftk arbeitszeitnachweis.pdf fill_form {filename}.fdf output {filename}.pdf")
	call(["pdftk", "arbeitszeitnachweis.pdf" ,"fill_form" , filename + ".fdf", "output", filename + ".pdf"], env = {"PATH": "./", "LD_LIBRARY_PATH": "./"})

	remove(filename + ".fdf")

	print(filename)