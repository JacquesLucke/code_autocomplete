import bpy
from bpy.props import *
from datetime import datetime
from .. graphics.utils import getDpiFactor
from . base import InsertTemplateBase, insert_template

class InsertLicense(bpy.types.Operator, InsertTemplateBase):
    bl_idname = "code_autocomplete.insert_license"
    bl_label = "Insert License"
    bl_description = ""

    author_name = StringProperty(name = "Name", default = bpy.context.user_preferences.system.author)
    author_mail = StringProperty(name = "eMail", default = "")

    def invoke(self, context, event):
        dpiFactor = getDpiFactor()
        return context.window_manager.invoke_props_dialog(self, 300 * dpiFactor, 200 * dpiFactor)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "author_name", text = "Name")
        layout.prop(self, "author_mail", text = "E-Mail")

    def execute(self, context):
        changes = {
            "YOUR_NAME" : self.author_name,
            "YOUR_MAIL" : self.author_mail,
            "CURRENT_YEAR" : str(datetime.now().year) }
        insert_template(license_template, changes)
        return {"FINISHED"}

license_template = """'''
Copyright (C) CURRENT_YEAR YOUR_NAME
YOUR_MAIL

Created by YOUR_NAME

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
"""
