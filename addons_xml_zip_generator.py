# *
# *  Copyright (C) 2012-2013 Garrett Brown
# *  Copyright (C) 2010      j48antialias
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *  Based on code by j48antialias:
# *  https://anarchintosh-projects.googlecode.com/files/addons_xml_generator.py

""" addons.xml generator """

import os
import sys

# Compatibility with 3.0, 3.1 and 3.2 not supporting u"" literals
if sys.version < '3':
    import codecs

    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x


class Generator:
    """
        Generates a new addons.xml file from each addons addon.xml file
        and a new addons.xml.md5 hash file. Must be run from the root of
        the checked-out repo. Only handles single depth folder structure.
    """

    def __init__(self):
        # generate files
        self._generate_addons_file()
        self._generate_md5_file()
        self._generate_zips()
        # notify user
        print("Finished updating addons xml and md5 files")

    def _generate_zips(self):
        # addon list
        addons = self._get_addons()

        # make sure we have repo dir
        os.system("mkdir -p repo")

        for addon in addons:
            if self._read_addon_xml(addon) is not False:
                os.system("mkdir -p repo/"+addon)
                version = self._read_version_number(self._read_addon_xml(addon))
                os.system("cp "+addon+"/fanart.jpg repo/"+addon)
                os.system("cp "+addon+"/icon.png repo/"+addon)
                os.system("cp "+addon+"/changelog.txt repo/"+addon)
                os.system("zip -9 -r repo/"+addon+"/"+addon+"-"+version+".zip " + addon)

    def _read_addon_xml(self, addon_path):
        # check for addon.xml and try and read it.
        addon_xml_path = os.path.join(addon_path, 'addon.xml')
        if os.path.exists(addon_xml_path):

            # load whole text into string
            f = open(addon_xml_path, "r")
            addon_xml = f.read()
            f.close()

            # return True if we found and read the addon.xml
            return addon_xml
        # return False if we couldn't  find the addon.xml
        else:
            return False

    def _read_version_number(self, addon_xml):
        # find the header of the addon.
        from lxml import etree
        root = etree.fromstring(addon_xml.encode("utf-8"))
        version = root.get("version")
        return version

    def _get_addons(self):
        addons = os.listdir(".")

        for directory in addons:
            if directory.startswith("."):
                print(directory)
                addons.remove(directory)
                continue
            if os.path.isdir(directory) is not True:
                addons.remove(directory)
                continue

        for addon in addons:
            try:
                # skip any file or .svn folder or .git folder
                if ( not os.path.isdir(addon) or addon == ".idea" or addon == ".git" ):
                    addons.remove(addon)
                    continue
                # create path
                _path = os.path.join(addon, "addon.xml")
                # split lines for stripping
                xml_lines = open(_path, "r").read().splitlines()
                # new addon

            except Exception as e:
                # missing or poorly formatted addon.xml
                print("Excluding %s for %s" % ( _path, e ))
                addons.remove(addon)


        return addons

    def _generate_addons_file(self):
        # addon list
        addons = os.listdir(".")
        # final addons text
        addons_xml = u("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<addons>\n")
        # loop thru and add each addons addon.xml file
        for addon in addons:
            try:
                # skip any file or .svn folder or .git folder
                if ( not os.path.isdir(addon) or addon == ".svn" or addon == ".git" ): continue
                # create path
                _path = os.path.join(addon, "addon.xml")
                # split lines for stripping
                xml_lines = open(_path, "r").read().splitlines()
                # new addon
                addon_xml = ""
                # loop thru cleaning each line
                for line in xml_lines:
                    # skip encoding format line
                    if ( line.find("<?xml") >= 0 ): continue
                    # add line
                    if sys.version < '3':
                        addon_xml += unicode(line.rstrip() + "\n", "UTF-8")
                    else:
                        addon_xml += line.rstrip() + "\n"
                    # we succeeded so add to our final addons.xml text
                addons_xml += addon_xml.rstrip() + "\n\n"
            except Exception as e:
                # missing or poorly formatted addon.xml
                print("Excluding %s for %s" % ( _path, e ))
            # clean and add closing tag
        addons_xml = addons_xml.strip() + u("\n</addons>\n")
        # save file
        self._save_file(addons_xml.encode("UTF-8"), file="addons.xml")

    def _generate_md5_file(self):
        # create a new md5 hash
        try:
            import md5

            m = md5.new(open("addons.xml", "r").read()).hexdigest()
        except ImportError:
            import hashlib

            m = hashlib.md5(open("addons.xml", "r", encoding="UTF-8").read().encode("UTF-8")).hexdigest()

        # save file
        try:
            self._save_file(m.encode("UTF-8"), file="addons.xml.md5")
        except Exception as e:
            # oops
            print("An error occurred creating addons.xml.md5 file!\n%s" % e)

    def _save_file(self, data, file):
        try:
            # write data to the file (use b for Python 3)
            open(file, "wb").write(data)
        except Exception as e:
            # oops
            print("An error occurred saving %s file!\n%s" % ( file, e ))


if ( __name__ == "__main__" ):
    # start
    Generator()