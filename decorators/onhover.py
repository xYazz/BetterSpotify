from kivy.core.window import Window
from kivy.uix.widget import Widget

def on_hover(class_to_decorate):
    

    
    class_to_decorate.register_event_type("on_enter")
    class_to_decorate.register_event_type("on_leave")
    Window.bind(mouse_pos=on_mouse_update)

    def on_mouse_update(*args):
        #  If the Widget currently has no parent, do nothing
        if not class_to_decorate.get_root_window():
            return
        pos = args[1]
        #
        #  is the pointer in the same position as the widget?
        #  If not - then issue an on_exit event if needed
        #
        if not class_to_decorate.collide_point(*class_to_decorate.to_widget(*pos)):
            class_to_decorate.hovering = False
            class_to_decorate.enter_point = None
            if class_to_decorate.hover_visible:
                class_to_decorate.hover_visible = False
                class_to_decorate.dispatch("on_leave")
            return

        #
        # The pointer is in the same position as the widget
        #

        if class_to_decorate.hovering:
            #
            #  nothing to do here. Not - this does not handle the case where
            #  a popup comes over an existing hover event.
            #  This seems reasonable
            #
            return

        #
        # Otherwise - set the hovering attribute
        #
        class_to_decorate.hovering = True

        #
        # We need to traverse the tree to see if the Widget is visible
        #
        # This is a two stage process:
        # - first go up the tree to the root Window.
        #   At each stage - check that the Widget is actually visible
        # - Second - At the root Window check that there is not another branch
        #   covering the Widget
        #

        class_to_decorate.hover_visible = True
        if class_to_decorate.detect_visible:
            widget: Widget = class_to_decorate
            while True:
                # Walk up the Widget tree from the target Widget
                parent = widget.parent
                try:
                    # See if the mouse point collides with the parent
                    # using both local and glabal coordinates to cover absoluet and relative layouts
                    pinside = parent.collide_point(
                        *parent.to_widget(*pos)
                    ) or parent.collide_point(*pos)
                except Exception:
                    # The collide_point will error when you reach the root Window
                    break
                if not pinside:
                    class_to_decorate.hover_visible = False
                    break
                # Iterate upwards
                widget = parent

            #
            #  parent = root window
            #  widget = first Widget on the current branch
            #

            children = parent.children
            for child in children:
                # For each top level widget - check if is current branch
                # If it is - then break.
                # If not then - since we start at 0 - this widget is visible
                #
                # Check to see if it should take the hover
                #
                if child == widget:
                    # this means that the current widget is visible
                    break
                if child.collide_point(*pos):
                    #  this means that the current widget is covered by a modal or popup
                    class_to_decorate.hover_visible = False
                    break
        if class_to_decorate.hover_visible:
            class_to_decorate.enter_point = pos
            class_to_decorate.dispatch("on_enter")

    def on_enter():
        """Called when mouse enters the bbox of the widget AND the widget is visible."""
        pass

    def on_leave():
        """Called when the mouse exits the widget AND the widget is visible."""
        pass
    return class_to_decorate

