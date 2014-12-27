Autocomplete - Unleash the Power of Scripting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To start the autocomplete function click the button in the left sidebar of the Text Editor. Now this button is replaced with ``Stop`` and ``Rebuild Documentation``. Rebuilding the documentation can be useful if you registered your own properties.

.. image:: start_button.png

.. image:: stop_button.png


If you start typing the autocomplete-box pops up and gives you suggestions. You can accept the selected one by pressing the TAB key or by clicking on it. Most of the time the addon notices when the autocomplete-box needs to be open. If you want to open/close it manually, just hit the ALT key.


Templates
*********

The addon comes with a few static templates which are shown if you typed specific patterns.
Here is a list with all currently available templates with example patterns to call them:

 1. **New Panel**
    ``class YourClassName(bpy.types.Panel):``
    ``class YourClassName(Panel):``
   
    .. code-block:: python
        :linenos:
        bl_idname = "name"
        bl_label = "label"
        bl_space_type = "VIEW_3D"
        bl_region_type = "TOOLS"
        bl_category = "category"
        
        def draw(self, context):
            layout = self.layout