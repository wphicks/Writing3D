"""Implementation of W3D-style timeline control in Blender"""

from .blender_trigger import TimedTrigger
import warnings
try:
    import bpy
except ImportError:
    warnings.warn(
        "Module bpy not found. \
Loading pycave.cave_logic.blender_trigger as standalone")

class BlenderTimeline(TimedTrigger):
    """A control structure within Blender for implementing timelines

    :param W3DTimeline timeline: The timeline to generate"""

    def get_object(self):
        """Create an empty object for timeline"""
        bpy.ops.object.add(
            type="EMPTY",
            layers=[layer == 20 for layer in range(1, 21)],
        )
        timeline_object = bpy.context.object
        timeline_object.name = self.blender_object_name
        return timeline_object

    def __init__(self, timeline):
        self.cave_timeline = timeline
        super(BlenderTimeline, self).__init__(
            self.cave_timeline["name"],
            self.cave_timeline["actions"][-1][0]
        )
        #NOPE! Not going to work if the last action in the timeline is at
        #duration 0
