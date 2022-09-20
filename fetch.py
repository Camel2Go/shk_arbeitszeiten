from requests import get
from subprocess import run

url_pdf = "https://www.verw.tu-dresden.de/verwricht/formulare/download.asp?file=Arbeitszeitnachweis%20Mindestlohngesetz.pdf"
url_vpn = "https://tu-dresden.de/zih/dienste/service-katalog/arbeitsumgebung/zugang_datennetz/vpn"
cookies = {}

def print_url(url, text):
	return f"\u001b]8;;{url}\u001b\\{text}\u001b]8;;\u001b\\"


print("[+] trying to fetch newest pdf from verw.tu-dresden.de...")
pdf = get(url_pdf)

# in case we are on the other side of the zih-firewall  
while not "application/pdf" in pdf.headers.get("Content-Type"):

	print("[!] couldn't fetch pdf, got \"" + pdf.headers.get("Content-Type") + "\" instead of \"application/pdf\"")
	print("[!] please either connect with " + print_url(url_vpn, "VPN") +", or go to " + print_url(url_pdf, "verw.tu-dresden.de") + ", login and paste presented link here")
	user = input("[#] (enter for vpn | paste url) > ")
	if "sid=" in user: cookies ["TuVerw"] = "tuvSID=" + user[user.index("sid=") + 4:]
	elif user: print("[!] wrong url, please paste the one presented under \"Bitte hier klicken, um die angeforderte Seite abzurufen.\" :)")
	pdf = get(url_pdf, cookies = cookies)
print("[+] successfully fetched pdf!")


print("[+] writing \"arbeitszeitnachweis.pdf\" to disk...", end="")
with open("arbeitszeitnachweis.pdf", "wb") as file:
	file.write(pdf.content)
print("done!")

print("[+] running qpdf to decrypt non-existent password...", end="")
run(["qpdf", "--decrypt", "--replace-input", "arbeitszeitnachweis.pdf"], check = True)
print("done!")
