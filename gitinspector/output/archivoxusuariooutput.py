# coding: utf-8
#
# Copyright © 2012-2015 Ejwa Software. All rights reserved.
#
# This file is part of gitinspector.
#
# gitinspector is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# gitinspector is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gitinspector. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
from __future__ import unicode_literals
import textwrap
from ..localization import N_
from .. import format, gravatar, terminal
from .. import archivoxusuario as archs
from .outputable import Outputable

RESPONSIBILITIES_INFO_TEXT = N_("The following responsibilities, by author, were found in the current "
                                "revision of the repository")
RECURSOS_INFO_TEXT = N_("The following resource participation percentage table, by author, was calculated")
ARCHIVOS_INFO_TEXT = N_("The following file participation percentage table, by author, was calculated")

def __output_row__html__(recursos, autores,tipo):
	timeline_html = "<table class=\"git full\" border=1 frame=void rules=rows><thead><tr>"
	if tipo == "recursos":
		timeline_html += "<th>Resource</th> <th>Author</th> <th>Percentage</th>"
	if tipo == "archivos":
		timeline_html += "<th>File</th> <th>Author</th> <th>Percentage</th>"
	timeline_html += "</tr></thead><tbody>"
	i = 0
	for recurso in recursos.items():
		colaboradores = []
		for j in range(len(recurso[1])):
			if recurso[1][j] > 0:
				col = {"nombre":autores[j],"porcentaje":recurso[1][j]}
				colaboradores.append(col)
		timeline_html += "<tr" + (" class=\"odd\">" if i % 2 == 1 else ">")
		timeline_html += "<td rowspan=\"+"+str(len(colaboradores))+"+\">" + recurso[0] + "</td>"
		timeline_html += "<td> "+ colaboradores[0].get("nombre")+"</td>"
		timeline_html += "<td>" + str(colaboradores[0].get("porcentaje"))+ "%</td>"
		timeline_html += "</tr>"
		for k in range(1,len(colaboradores)):
			timeline_html += "<tr" + (" class=\"odd\">" if i % 2 == 1 else ">")
			timeline_html += "<td> "+ colaboradores[k].get("nombre")+"</td>"
			timeline_html += "<td>" + str(colaboradores[k].get("porcentaje"))+ "%</td>"
			timeline_html += "</tr>"
		i = i + 1

	timeline_html += "</tbody></table>"
	print(timeline_html)


class ArchivoXUsuarioOutput(Outputable):
	def __init__(self, changes, blame,ignorar,tipo):
		self.changes = changes
		self.blame = blame
		self.ignorar = ignorar
		self.tipo = tipo
		Outputable.__init__(self)

	def output_json(self):

		message_json = "\t\t\"message\": \"" + _(RESPONSIBILITIES_INFO_TEXT) + "\",\n"
		resp_json = ""

		autores = sorted(set(i[0] for i in self.blame.blames))
		for author in autores:
			if self.changes.get_latest_email_by_author(author) in self.ignorar:
				temp = []
				for aut in autores:
					if not aut == author:
						temp.append(aut)
				autores = temp
		tabla = archs.AutorXUsuario.get(self.blame,	autores)
		for arch in tabla.items():
			resp_json += "{\n"
			resp_json += "\t\t\t\"file\": \"" + arch[0] + "\",\n"
			resp_json += "\t\t\t\"authors\": [\n\t\t\t"
			if sum(arch[1]) > 0:
				for k in range(len(arch[1])):
					if arch[1][k] >0 :
						resp_json += "{\n"
						resp_json += "\t\t\t\t\"name\": \"" + autores[k] + "\",\n"
						resp_json += "\t\t\t\t\"email\": \"" + self.changes.get_latest_email_by_author(autores[k]) + "\",\n"
						resp_json += "\t\t\t\t\"rows\": " + str(arch[1][k]) + "\n"
						resp_json += "\t\t\t},"
			resp_json = resp_json[:-1]
			resp_json += "]\n\t\t},"
		resp_json = resp_json[:-1]
		print(",\n\t\"responsibilities\": {\n" + message_json + "\t\t\"files\": [\n\t\t" + resp_json + "]\n\t}", end="")

	def output_html(self):
		autores = sorted(set(i[0] for i in self.blame.blames))
		for author in autores:
			if self.changes.get_latest_email_by_author(author) in self.ignorar:
				temp = []
				for aut in autores:
					if not aut == author:
						temp.append(aut)
				autores = temp
		tabla = archs.AutorXUsuario.get(self.blame,	autores)
		recursos = {}
		if self.tipo == "recursos":
			for arch in tabla.items():
				if "src/app/" in arch[0]:
					path = arch[0].replace("src/app/","")
					if "/" in path:
						recurso = path.split("/")[0]
						if recurso not in recursos:
							recursos[recurso] = arch[1]
						else:
							for k in range(len(arch[1])):
								recursos[recurso][k] += arch[1][k]
		if self.tipo == "archivos":
			for arch in tabla.items():
				recursos[arch[0].replace("/src/main/java/co/edu/uniandes/csw","").replace("/src/test/java/co/edu/uniandes/csw","")] = arch[1]

		for recurso in recursos.items():
			total = sum(recurso[1])
			for i in range(len(recurso[1])):
				recurso[1][i] = round((recurso[1][i]/total)*100,2)

		archivos_html = "<div><div id=\"archivosxusuarios\" class=\"box\">"
		if self.tipo == "recursos":
			archivos_html += "<p>" + _(RECURSOS_INFO_TEXT) + ".</p>"
		if self.tipo == "archivos":
			archivos_html += "<p>" + _(ARCHIVOS_INFO_TEXT) + ".</p>"
		print(archivos_html)
		__output_row__html__(recursos, autores,self.tipo)
		archivos_html = "</div></div>"
		print(archivos_html)
