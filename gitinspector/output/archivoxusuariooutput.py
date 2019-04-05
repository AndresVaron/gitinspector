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

ARCHIVOS_INFO_TEXT = N_("Lo siguente corresponde a la tabla de modificaciones por usuarios en cada archivo, "
                        "Ademas se genera una tabla por herarquia (dfs)")

class ArchivoXUsuarioOutput(Outputable):
	def __init__(self, changes, blame):
		self.changes = changes
		self.blame = blame
		Outputable.__init__(self)

	def output_text(self):
		print("\n" + textwrap.fill(_(ARCHIVOS_INFO_TEXT) + ":", width=terminal.get_size()[0]))
#		Se envia el blame y la lista de autores ordenada
		authors = sorted(set(i[0] for i in self.blame.blames))
		tabla = archs.AutorXUsuario.get(self.blame,	authors)
		recursos = {}
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
		for recurso in recursos.items():
			total = sum(recurso[1])
			for i in range(len(recurso[1])):
				recurso[1][i] = round(recurso[1][i]/total,4)
		print(authors)
		print(recursos)

	def output_html(self):
		print("ok!")
