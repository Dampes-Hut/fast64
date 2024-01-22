import bpy


class OoTPointLightPanel(bpy.types.Panel):
    bl_label = "Fast64 OoT Point Light"
    bl_idname = "OBJECT_PT_fast64_oot_point_light"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return context.light and context.light.type == "POINT"

    def draw(self, context):
        self.layout.prop(context.light, "er_lights_ui_isGlow")


def register():
    bpy.utils.register_class(OoTPointLightPanel)
    bpy.types.Light.er_lights_ui_isGlow = bpy.props.BoolProperty("Draw Glow", default=True)


def unregister():
    bpy.utils.unregister_class(OoTPointLightPanel)
