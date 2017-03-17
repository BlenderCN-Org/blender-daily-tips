# -----------------------------------------------------------------------------
# Blender Tips - Addon for daily blender tips
# Developed by Patrick W. Crawford
#

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# -----------------------------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------------------------

import bpy

# updater ops import, all setup in this file
from . import conf
from . import BDT_updater_ops
from . import BDT_requests


# -----------------------------------------------------------------------------
# PANELS AND POPUPS
# -----------------------------------------------------------------------------


class BDT_get_tips(bpy.types.Operator):
	"""Call which will popup tips after fetching from online"""
	bl_label = "Get blender tips"
	bl_idname = "dailytips.get_tips"
	{'REGISTER','UNDO'}

	def execute(self, context):

		res = BDT_requests.check_tip_async(self, context)
		self.report(*res)

		return {"FINISHED"}



class BDT_show_tips(bpy.types.Operator):
	"""Call which will popup tips in a floating window"""
	bl_label = "Blender Daily Tips"
	bl_idname = "dailytips.show_tips"
	{'REGISTER','UNDO'}

	def invoke(self, context, event):
		# No OK button, will auto-execute code
		return context.window_manager.invoke_popup(self)

	def draw(self, context):
		layout = self.layout
		layout.lable("Daily tip!!!")

		## COL1
		# icon left gallery view of tips
		# operator to open video below

		## COL2
		# preview text from video via API
		# Channel / "Tweet this!"

		# label: Change feed and popup frequency in settings
		# open settings button

	def execute(self, context):
		return {'FINISHED'}



def bdt_draw_preferences(self, context):
	"""Preferences draw function"""
	layout = self.layout
	split = layout.split(percentage=0.6)
	topcol = split.column()
	box = topcol.box()
	box.label("Tip Frequency")
	col = box.column()
	col.prop(self,"auto_show_tips")
	col = box.column()
	col.enabled = self.auto_show_tips
	col.prop(self,"auto_show_frequency",text="Frequency (days)")


	# section for updater code, not yet configured
	topcol = split.column()
	# makes its own box

	# updater draw function
	BDT_updater_ops.update_settings_ui(self,context,topcol)


def bdt_helptip_draw_append(self, context):
	"""Function to add operator to help dropdown of info window"""
	self.layout.operator("dailytips.get_tips")




# -----------------------------------------------------------------------------
# PROPERTYS AND PREFRENCES
# -----------------------------------------------------------------------------

# scene-saved settings
# class btd_props_scene(bpy.types.PropertyGroup):
#
# 	x = bpy.props.BoolProperty(
# 		name = "x",
# 		description = "x",
# 		default = False)


class BDT_preferences(bpy.types.AddonPreferences):
	bl_idname = __package__
	
	auto_show_tips = bpy.props.BoolProperty(
		name = "Auto show tips",
		description = "If enabled, auto-check latest tips once a day at most",
		default = True,
		)
	auto_show_frequency = bpy.props.IntProperty(
		name='Tip frequency (days)',
		description = "Number of days between auto-checking for tips, select 1 for daily",
		default=1,
		min=1,
		)

	
	# tip subscription sources

	tips_blendernation = bpy.props.BoolProperty(
		name = "Blendernation Tutorial",
		description = "Get the latest tutorial posted on Blender Nation",
		default = False,
		)

	tips_yanal_sosak = bpy.props.BoolProperty(
		name = "Yanal Sosak Daily Tips",
		description = "Received daily tips from Yanal Sosak",
		default = True,
		)

	# addon updater preferences

	updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description = "Number of days between checking for updates",
		default=7,
		min=0,
		)

	auto_check_update = bpy.props.BoolProperty(
		name = "Auto-check for Update",
		description = "If enabled, auto-check for updates using an interval",
		default = False,
		)
	
	updater_intrval_months = bpy.props.IntProperty(
		name='Months',
		description = "Number of months between checking for updates",
		default=0,
		min=0
		)
	updater_intrval_days = bpy.props.IntProperty(
		name='Days',
		description = "Number of days between checking for updates",
		default=7,
		min=0,
		)
	updater_intrval_hours = bpy.props.IntProperty(
		name='Hours',
		description = "Number of hours between checking for updates",
		default=0,
		min=0,
		max=23
		)
	updater_intrval_minutes = bpy.props.IntProperty(
		name='Minutes',
		description = "Number of minutes between checking for updates",
		default=0,
		min=0,
		max=59
		)

	def draw(self, context):
		bdt_draw_preferences(self, context)


# -----------------------------------------------------------------------------
# REGISTER
# -----------------------------------------------------------------------------


def register():

	bpy.utils.register_class(BDT_get_tips)
	bpy.utils.register_class(BDT_show_tips)
	bpy.utils.register_class(BDT_preferences)

	bpy.types.INFO_MT_help.append(bdt_helptip_draw_append)
	


def unregister():

	bpy.utils.unregister_class(BDT_get_tips)
	bpy.utils.unregister_class(BDT_show_tips)
	bpy.utils.unregister_class(BDT_preferences)

	bpy.types.INFO_MT_help.remove(bdt_helptip_draw_append)
	
