from subprocess import Popen, PIPE
from sys import argv
import re, pprint, csv, time


start = time.time()

_, osname = argv

libraries = {}
libraries[osname] = {}
binaries = {}

SEARCH_PATHS = ["/usr/lib64", "/usr/lib", "/usr/bin"]

search_terms = ["firefox*", "chromi*", "audacity*", "keepass*", "soffice*", "gimp*", "inks*", "vlc*"]
app_names = ["Firefox", "Chromium", "Audacity", "Keepassxc", "Libreoffice", "GIMP", "InkScape", "VLC"]


for name in app_names:
  binaries[name] = []


# Find path to app binaries
for (search, name) in zip(search_terms, app_names):
  find_proc = Popen(['find', SEARCH_PATHS[0], SEARCH_PATHS[1], \
                  SEARCH_PATHS[2], '-name', search], stdout=PIPE, stderr=PIPE)

  paths, find_err = find_proc.communicate()
  paths = paths.decode("utf-8").split("\n")

  if find_err:
    find_err = find_err.decode("utf-8")
    print("!!! ERROR (", name,"): ", find_err)

  for path in paths:
    file_proc = Popen(['file', path], stdout=PIPE, stdin=PIPE)

    filetype, file_err = file_proc.communicate()
    filetype = filetype.decode("utf-8")

    if file_err:
      file_err = file_err.decode("utf-8")
      print("!!! ERROR (", path, "): ", file_err)

    # check for ELF binaries, ignore plugins if possible
    if "ELF" in filetype and "interpreter" in filetype and "plug" not in path:
      binaries[name].append(path)


for name in binaries:
  count = 0
  oldbinary = ""
  for binary in binaries[name]:
    ldd_proc = Popen(['ldd', binary], stdout=PIPE, stderr=PIPE)

    libs, ldd_err = ldd_proc.communicate()
    libs = libs.decode("utf-8")

    if ldd_err:
      ldd_err = ldd_err.decode("utf-8")
      print("!!! ERROR (", name,"): ", ldd_err)

    if count > 0:
      binary = oldbinary

    libs_regex = re.findall("(?<!\/)(?<![a-z])(lib.+?|ld.+?)(?=\.so)", libs)

    if name not in libraries[osname]:
      libraries[osname][name] = set(["ld-linux-x86-64"])

    libraries[osname][name].update(libs_regex)

    count += 1
    oldbinary = binary


with open('libraries.csv', 'a') as f:
    writer = csv.writer(f, delimiter=' ')
    for os in libraries.keys():
        for app in libraries[os]:
            for lib in libraries[os][app]:
                writer.writerow([os, app, lib])

end = time.time()
print(end - start)
