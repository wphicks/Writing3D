"""Tools for working with sounds in Cave projects
"""
from features import CaveFeature
from validators import AlwaysValid, IsNumeric, OptionListValidator


class CaveSound(CaveFeature):
    """Store data on a sound to be used in the Cave

    :param str name: Unique name of this sound object
    :param str filename: File from which to take audio
    :param bool autostart: Start sound when project starts?
    :param str movement_mode: One of Positional or Fixed, determining if the
    sound is ambient or coming from an apparent position
    :param int repetitions: Number of times to repeat sound. Negative value
    indicates sound should loop forever
    :param float frequency_scale: Factor by which to scale frequency
    :param float volume_scale: Factor by which to scale volume (must be
    0.0-1.0)
    :param float pan: Stereo panning left to right (-1.0 to 1.0)
    """
    argument_validators = {
        "name": AlwaysValid(
            help_string="This should be a string specifying a unique name for"
            " this sound"),
        "filename": AlwaysValid(
            help_string="This should be a string specifying the audio file"),
        "autostart": AlwaysValid(help_string="Either true or false"),
        "movement_mode": OptionListValidator("Positional", "Fixed"),
        "repetitions": IsNumeric(),
        "frequency_scale": IsNumeric(min_value=0),
        "volume_scale": IsNumeric(min_value=0, max_value=1),
        "pan": IsNumeric(min_value=-1, max_value=1)
        }
    default_arguments = {
        "autostart": False,
        "movement_mode": "Positional",
        "repetitions": 0,
        "frequency_scale": 1,
        "volume_scale": 1,
        "pan": 0}

    def toXML(self, all_sounds_root):
        """Store CaveSound as Sound node within SoundRoot node

        :param :py:class:xml.etree.ElementTree.Element all_sounds_root
        """
        CaveFeature.toXML(self, all_sounds_root)  # TODO: Replace this

    @classmethod
    def fromXML(sound_root):
        """Create CaveSound from Sound node

        :param :py:class:xml.etree.ElementTree.Element object_root
        """
        return CaveFeature.fromXML(sound_root)  # TODO: Replace this

    def blend(self):
        """Create representation of CaveSound in Blender"""
        raise NotImplementedError  # TODO
