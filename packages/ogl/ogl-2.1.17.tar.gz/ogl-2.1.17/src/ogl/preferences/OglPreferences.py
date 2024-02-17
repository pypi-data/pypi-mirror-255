
from pathlib import Path
from typing import Dict
from typing import List

from logging import Logger
from logging import getLogger

from configparser import ConfigParser

from codeallybasic.SingletonV3 import SingletonV3
from codeallybasic.ConfigurationLocator import ConfigurationLocator

from miniogl.MiniOglColorEnum import MiniOglColorEnum
from miniogl.MiniOglPenStyle import MiniOglPenStyle

from ogl.OglDimensions import OglDimensions
from ogl.OglTextFontFamily import OglTextFontFamily

OGL_PREFS_NAME_VALUES = Dict[str, str]


class OglPreferences(metaclass=SingletonV3):

    MODULE_NAME:            str = 'ogl'
    PREFERENCES_FILENAME:   str = f'{MODULE_NAME}.ini'

    SECTION_OGL_PREFERENCES:  str = 'Ogl'
    SECTION_DIAGRAM:          str = 'Diagram'
    SECTION_NAMES:            str = 'Names'
    SECTION_SEQUENCE_DIAGRAM: str = 'SequenceDiagrams'
    SECTION_ASSOCIATIONS:     str = 'Associations'
    SECTION_DEBUG:            str = 'Debug'

    SECTIONS: List[str] = [SECTION_OGL_PREFERENCES, SECTION_DIAGRAM, SECTION_NAMES, SECTION_SEQUENCE_DIAGRAM, SECTION_ASSOCIATIONS, SECTION_DEBUG]

    NOTE_TEXT:        str = 'note_text'
    NOTE_DIMENSIONS:  str = 'note_dimensions'
    TEXT_DIMENSIONS:  str = 'text_dimensions'
    TEXT_BOLD:        str = 'text_bold'
    TEXT_ITALICIZE:   str = 'text_italicize'
    TEXT_FONT_FAMILY: str = 'text_font_family'
    TEXT_FONT_SIZE:   str = 'text_font_size'
    TEXT_VALUE:       str = 'text_value'
    CLASS_DIMENSIONS: str = 'class_dimensions'
    CLASS_BACKGROUND_COLOR: str = 'class_background_color'
    CLASS_TEXT_COLOR:       str = 'class_text_color'
    DISPLAY_DUNDER_METHODS: str = 'display_dunder_methods'
    DISPLAY_CONSTRUCTOR:    str = 'display_constructor'

    DEFAULT_CLASS_BACKGROUND_COLOR: str = MiniOglColorEnum.MINT_CREAM.value
    DEFAULT_CLASS_TEXT_COLOR:       str = MiniOglColorEnum.BLACK.value

    # noinspection SpellCheckingInspection
    OGL_PREFERENCES: OGL_PREFS_NAME_VALUES = {
        NOTE_TEXT:              'This is the note text',
        NOTE_DIMENSIONS:        OglDimensions(100, 50).__str__(),
        TEXT_DIMENSIONS:        OglDimensions(125, 50).__str__(),
        TEXT_BOLD:              'False',
        TEXT_ITALICIZE:         'False',
        TEXT_FONT_FAMILY:       'Swiss',
        TEXT_FONT_SIZE:         '14',
        TEXT_VALUE:             'Donec eleifend luctus enim vel mollis',
        CLASS_DIMENSIONS:        OglDimensions(150, 75).__str__(),
        CLASS_BACKGROUND_COLOR:  DEFAULT_CLASS_BACKGROUND_COLOR,
        CLASS_TEXT_COLOR:        DEFAULT_CLASS_TEXT_COLOR,
        DISPLAY_CONSTRUCTOR:     'True',
        DISPLAY_DUNDER_METHODS:  'True',
    }

    DEFAULT_GRID_LINE_COLOR: str = MiniOglColorEnum.LIGHT_GREY.value
    DEFAULT_GRID_LINE_STYLE: str = MiniOglPenStyle.DOT.value

    BACKGROUND_GRID_ENABLED:  str = 'background_grid_enabled'
    SNAP_TO_GRID:             str = 'snap_to_grid'
    BACKGROUND_GRID_INTERVAL: str = 'background_grid_interval'
    GRID_LINE_COLOR:          str = 'grid_line_color'
    GRID_LINE_STYLE:          str = 'grid_line_style'
    CENTER_DIAGRAM:           str = 'center_diagram'
    SHOW_PARAMETERS:          str = 'show_parameters'

    DIAGRAM_PREFERENCES: OGL_PREFS_NAME_VALUES = {
        CENTER_DIAGRAM:          'False',
        BACKGROUND_GRID_ENABLED: 'True',
        SNAP_TO_GRID:            'True',
        SHOW_PARAMETERS:         'False',
        BACKGROUND_GRID_INTERVAL: '25',
        GRID_LINE_COLOR:          DEFAULT_GRID_LINE_COLOR,
        GRID_LINE_STYLE:          DEFAULT_GRID_LINE_STYLE
    }

    DEFAULT_CLASS_NAME:     str = 'default_class_name'
    DEFAULT_NAME_INTERFACE: str = 'default_name_interface'
    DEFAULT_NAME_USECASE:   str = 'default_name_usecase'
    DEFAULT_NAME_ACTOR:     str = 'default_name_actor'
    DEFAULT_NAME_METHOD:    str = 'default_name_method'
    DEFAULT_NAME_FIELD:     str = 'default_name_field'
    DEFAULT_NAME_PARAMETER: str = 'default_name_parameter'

    NAME_PREFERENCES: OGL_PREFS_NAME_VALUES = {
        DEFAULT_CLASS_NAME:     'ClassName',
        DEFAULT_NAME_INTERFACE: 'IClassInterface',
        DEFAULT_NAME_USECASE:   'UseCaseName',
        DEFAULT_NAME_ACTOR:     'ActorName',
        DEFAULT_NAME_METHOD:    'MethodName',
        DEFAULT_NAME_FIELD:     'FieldName',
        DEFAULT_NAME_PARAMETER: 'ParameterName',
    }

    INSTANCE_Y_POSITION: str = 'instance_y_position'
    INSTANCE_DIMENSIONS: str = 'instance_dimensions'

    SEQUENCE_DIAGRAM_PREFERENCES: OGL_PREFS_NAME_VALUES = {
        INSTANCE_Y_POSITION: '50',
        INSTANCE_DIMENSIONS: OglDimensions(100, 400).__str__(),
    }

    DIAMOND_SIZE: str = 'diamond_size'

    ASSOCIATION_PREFERENCES: OGL_PREFS_NAME_VALUES = {
        TEXT_FONT_SIZE: '12',
        DIAMOND_SIZE:   '7',
    }

    DEBUG_DIAGRAM_FRAME:           str = 'debug_diagram_frame'
    DEBUG_BASIC_SHAPE:             str = 'debug_basic_shape'              # If `True` turn on debug display code in basic Shape.py

    DEBUG_PREFERENCES: OGL_PREFS_NAME_VALUES = {
        DEBUG_DIAGRAM_FRAME: 'False',
        DEBUG_BASIC_SHAPE:   'False',
    }

    def __init__(self):

        self.logger:  Logger       = getLogger(__name__)
        self._config: ConfigParser = ConfigParser()

        cl:                        ConfigurationLocator = ConfigurationLocator()
        self._preferencesFileName: Path                 = cl.applicationPath(f'{OglPreferences.MODULE_NAME}') / OglPreferences.PREFERENCES_FILENAME

        self._loadPreferences()

    @property
    def noteText(self) -> str:
        return self._config.get(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.NOTE_TEXT)

    @noteText.setter
    def noteText(self, theNewValue: str):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.NOTE_TEXT, theNewValue)
        self._saveConfig()

    @property
    def noteDimensions(self) -> OglDimensions:
        serializedDimensions: str = self._config.get(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.NOTE_DIMENSIONS)
        return OglDimensions.deSerialize(serializedDimensions)

    @noteDimensions.setter
    def noteDimensions(self, newValue: OglDimensions):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.NOTE_DIMENSIONS, newValue.__str__())
        self._saveConfig()

    @property
    def textDimensions(self) -> OglDimensions:
        serializedDimensions: str = self._config.get(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_DIMENSIONS)
        return OglDimensions.deSerialize(serializedDimensions)

    @textDimensions.setter
    def textDimensions(self, newValue: OglDimensions):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_DIMENSIONS, newValue.__str__())
        self._saveConfig()

    @property
    def textBold(self) -> bool:
        return self._config.getboolean(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_BOLD)

    @textBold.setter
    def textBold(self, newValue: bool):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_BOLD, str(newValue))
        self._saveConfig()

    @property
    def textItalicize(self) -> bool:
        return self._config.getboolean(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_ITALICIZE)

    @textItalicize.setter
    def textItalicize(self, newValue: bool):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_ITALICIZE, str(newValue))
        self._saveConfig()

    @property
    def textFontFamily(self) -> OglTextFontFamily:
        """

        Returns: The Text Font Family
        """

        fontStr: str = self._config.get(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_FONT_FAMILY)

        fontEnum: OglTextFontFamily = OglTextFontFamily(fontStr)

        return fontEnum

    @textFontFamily.setter
    def textFontFamily(self, newValue: OglTextFontFamily):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_FONT_FAMILY, newValue.value)
        self._saveConfig()

    @property
    def textFontSize(self) -> int:
        return self._config.getint(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_FONT_SIZE)

    @textFontSize.setter
    def textFontSize(self, newValue: int):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_FONT_SIZE, str(newValue))
        self._saveConfig()

    @property
    def textValue(self) -> str:
        return self._config.get(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_VALUE)

    @textValue.setter
    def textValue(self, newValue: str):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.TEXT_VALUE, newValue)
        self._saveConfig()

    @property
    def classDimensions(self) -> OglDimensions:
        serializedDimensions: str = self._config.get(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.CLASS_DIMENSIONS)
        return OglDimensions.deSerialize(serializedDimensions)

    @classDimensions.setter
    def classDimensions(self, newValue: OglDimensions):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.CLASS_DIMENSIONS, newValue.__str__())
        self._saveConfig()

    @property
    def classBackgroundColor(self) -> MiniOglColorEnum:
        colorName:     str           = self._config.get(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.CLASS_BACKGROUND_COLOR)
        pyutColorEnum: MiniOglColorEnum = MiniOglColorEnum(colorName)
        return pyutColorEnum

    @classBackgroundColor.setter
    def classBackgroundColor(self, newValue: MiniOglColorEnum):
        colorName: str = newValue.value
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.CLASS_BACKGROUND_COLOR, colorName)
        self._saveConfig()

    @property
    def classTextColor(self) -> MiniOglColorEnum:
        colorName:     str           = self._config.get(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.CLASS_TEXT_COLOR)
        pyutColorEnum: MiniOglColorEnum = MiniOglColorEnum(colorName)
        return pyutColorEnum

    @classTextColor.setter
    def classTextColor(self, newValue: MiniOglColorEnum):
        colorName: str = newValue.value
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.CLASS_TEXT_COLOR, colorName)

        self._saveConfig()

    @property
    def displayDunderMethods(self) -> bool:
        return self._config.getboolean(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.DISPLAY_DUNDER_METHODS)

    @displayDunderMethods.setter
    def displayDunderMethods(self, newValue: bool):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.DISPLAY_DUNDER_METHODS, str(newValue))
        self._saveConfig()

    @property
    def displayConstructor(self) -> bool:
        return self._config.getboolean(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.DISPLAY_CONSTRUCTOR)

    @displayConstructor.setter
    def displayConstructor(self, newValue: bool):
        self._config.set(OglPreferences.SECTION_OGL_PREFERENCES, OglPreferences.DISPLAY_CONSTRUCTOR, str(newValue))
        self._saveConfig()

    @property
    def className(self) -> str:
        return self._config.get(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_CLASS_NAME)

    @className.setter
    def className(self, newValue: str):
        self._config.set(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_CLASS_NAME, str(newValue))
        self._saveConfig()

    @property
    def interfaceName(self) -> str:
        return self._config.get(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_INTERFACE)

    @interfaceName.setter
    def interfaceName(self, newValue: str):
        self._config.set(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_INTERFACE, newValue)
        self._saveConfig()

    @property
    def useCaseName(self) -> str:
        return self._config.get(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_USECASE)

    @useCaseName.setter
    def useCaseName(self, newValue: str):
        self._config.set(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_USECASE, newValue)
        self._saveConfig()

    @property
    def actorName(self) -> str:
        return self._config.get(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_ACTOR)

    @actorName.setter
    def actorName(self, newValue: str):
        self._config.set(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_ACTOR, newValue)
        self._saveConfig()

    @property
    def methodName(self) -> str:
        return self._config.get(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_METHOD)

    @methodName.setter
    def methodName(self, newValue: str):
        self._config.set(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_METHOD, newValue)
        self._saveConfig()

    @property
    def fieldName(self) -> str:
        return self._config.get(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_FIELD)

    @fieldName.setter
    def fieldName(self, newValue: str):
        self._config.set(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_FIELD, newValue)
        self._saveConfig()

    @property
    def parameterName(self) -> str:
        return self._config.get(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_PARAMETER)

    @parameterName.setter
    def parameterName(self, newValue: str):
        self._config.set(OglPreferences.SECTION_NAMES, OglPreferences.DEFAULT_NAME_PARAMETER, newValue)
        self._saveConfig()

    @property
    def centerDiagram(self):
        centerDiagram: bool = self._config.getboolean(OglPreferences.SECTION_DIAGRAM, OglPreferences.CENTER_DIAGRAM)
        return centerDiagram

    @centerDiagram.setter
    def centerDiagram(self, theNewValue: bool):
        self._config.set(OglPreferences.SECTION_DIAGRAM, OglPreferences.CENTER_DIAGRAM, str(theNewValue))
        self._saveConfig()

    @property
    def backgroundGridEnabled(self) -> bool:
        return self._config.getboolean(OglPreferences.SECTION_DIAGRAM, OglPreferences.BACKGROUND_GRID_ENABLED)

    @backgroundGridEnabled.setter
    def backgroundGridEnabled(self, theNewValue: bool):
        self._config.set(OglPreferences.SECTION_DIAGRAM, OglPreferences.BACKGROUND_GRID_ENABLED, str(theNewValue))
        self._saveConfig()

    @property
    def snapToGrid(self) -> bool:
        return self._config.getboolean(OglPreferences.SECTION_DIAGRAM, OglPreferences.SNAP_TO_GRID)

    @snapToGrid.setter
    def snapToGrid(self, theNewValue: bool):
        self._config.set(OglPreferences.SECTION_DIAGRAM, OglPreferences.SNAP_TO_GRID, str(theNewValue))
        self._saveConfig()

    @property
    def backgroundGridInterval(self) -> int:
        return self._config.getint(OglPreferences.SECTION_DIAGRAM, OglPreferences.BACKGROUND_GRID_INTERVAL)

    @backgroundGridInterval.setter
    def backgroundGridInterval(self, theNewValue: int):
        self._config.set(OglPreferences.SECTION_DIAGRAM, OglPreferences.BACKGROUND_GRID_INTERVAL, str(theNewValue))
        self._saveConfig()

    @property
    def showParameters(self) -> bool:
        return self._config.getboolean(OglPreferences.SECTION_DIAGRAM, OglPreferences.SHOW_PARAMETERS)

    @showParameters.setter
    def showParameters(self, theNewValue: bool):
        self._config.set(OglPreferences.SECTION_DIAGRAM, OglPreferences.SHOW_PARAMETERS, str(theNewValue))
        self._saveConfig()

    @property
    def gridLineColor(self) -> MiniOglColorEnum:

        colorName:     str           = self._config.get(OglPreferences.SECTION_DIAGRAM, OglPreferences.GRID_LINE_COLOR)
        pyutColorEnum: MiniOglColorEnum = MiniOglColorEnum(colorName)
        return pyutColorEnum

    @gridLineColor.setter
    def gridLineColor(self, theNewValue: MiniOglColorEnum):

        colorName: str = theNewValue.value
        self._config.set(OglPreferences.SECTION_DIAGRAM, OglPreferences.GRID_LINE_COLOR, colorName)
        self._saveConfig()

    @property
    def gridLineStyle(self) -> MiniOglPenStyle:
        penStyleName: str          = self._config.get(OglPreferences.SECTION_DIAGRAM, OglPreferences.GRID_LINE_STYLE)
        pyutPenStyle: MiniOglPenStyle = MiniOglPenStyle(penStyleName)
        return pyutPenStyle

    @gridLineStyle.setter
    def gridLineStyle(self, theNewValue: MiniOglPenStyle):

        penStyleName: str = theNewValue.value
        self._config.set(OglPreferences.SECTION_DIAGRAM, OglPreferences.GRID_LINE_STYLE, penStyleName)
        self._saveConfig()

    @property
    def instanceYPosition(self) -> int:
        return self._config.getint(OglPreferences.SECTION_SEQUENCE_DIAGRAM, OglPreferences.INSTANCE_Y_POSITION)

    @instanceYPosition.setter
    def instanceYPosition(self, newValue: int):
        self._config.set(OglPreferences.SECTION_SEQUENCE_DIAGRAM, OglPreferences.INSTANCE_Y_POSITION, str(newValue))
        self._saveConfig()

    @property
    def instanceDimensions(self) -> OglDimensions:
        serializedDimensions: str = self._config.get(OglPreferences.SECTION_SEQUENCE_DIAGRAM, OglPreferences.INSTANCE_DIMENSIONS)
        return OglDimensions.deSerialize(serializedDimensions)

    @instanceDimensions.setter
    def instanceDimensions(self, newValue: OglDimensions):
        self._config.set(OglPreferences.SECTION_SEQUENCE_DIAGRAM, OglPreferences.INSTANCE_DIMENSIONS, newValue.__str__())
        self._saveConfig()

    @property
    def associationDiamondSize(self) -> int:
        return self._config.getint(OglPreferences.SECTION_ASSOCIATIONS, OglPreferences.DIAMOND_SIZE)

    @associationDiamondSize.setter
    def associationDiamondSize(self, newValue: int):
        self._config.set(OglPreferences.SECTION_ASSOCIATIONS, OglPreferences.DIAMOND_SIZE, str(newValue))
        self._saveConfig()

    @property
    def associationTextFontSize(self) -> int:
        return self._config.getint(OglPreferences.SECTION_ASSOCIATIONS, OglPreferences.TEXT_FONT_SIZE)

    @associationTextFontSize.setter
    def associationTextFontSize(self, newValue: int):
        self._config.set(OglPreferences.SECTION_ASSOCIATIONS, OglPreferences.TEXT_FONT_SIZE, str(newValue))
        self._saveConfig()

    @property
    def debugDiagramFrame(self) -> bool:
        ans: bool = self._config.getboolean(OglPreferences.SECTION_DEBUG, OglPreferences.DEBUG_DIAGRAM_FRAME)
        return ans

    @debugDiagramFrame.setter
    def debugDiagramFrame(self, theNewValue: bool):
        self._config.set(OglPreferences.SECTION_DEBUG, OglPreferences.DEBUG_DIAGRAM_FRAME, str(theNewValue))
        self._saveConfig()

    @property
    def debugBasicShape(self):
        ans: bool = self._config.getboolean(OglPreferences.SECTION_DEBUG, OglPreferences.DEBUG_BASIC_SHAPE)
        return ans

    @debugBasicShape.setter
    def debugBasicShape(self, theNewValue: bool):
        self._config.set(OglPreferences.SECTION_DEBUG, OglPreferences.DEBUG_BASIC_SHAPE, str(theNewValue))
        self._saveConfig()

    def _loadPreferences(self):

        self._ensurePreferenceFileExists()

        # Read data
        self._config.read(self._preferencesFileName)
        self._addMissingPreferences()
        self._saveConfig()

    def _ensurePreferenceFileExists(self):

        try:
            f = open(self._preferencesFileName, "r")
            f.close()
        except (ValueError, Exception):
            try:
                f = open(self._preferencesFileName, "w")
                f.write("")
                f.close()
                self.logger.warning(f'Preferences file re-created')
            except (ValueError, Exception) as e:
                self.logger.error(f"Error: {e}")
                return

    def _addMissingPreferences(self):

        try:
            self._addMissingSections()

            # key: section name, value: section dictionary
            preferenceSections: Dict[str, OGL_PREFS_NAME_VALUES] = {
                OglPreferences.SECTION_OGL_PREFERENCES:  OglPreferences.OGL_PREFERENCES,
                OglPreferences.SECTION_DIAGRAM:          OglPreferences.DIAGRAM_PREFERENCES,
                OglPreferences.SECTION_NAMES:            OglPreferences.NAME_PREFERENCES,
                OglPreferences.SECTION_SEQUENCE_DIAGRAM: OglPreferences.SEQUENCE_DIAGRAM_PREFERENCES,
                OglPreferences.SECTION_ASSOCIATIONS:     OglPreferences.ASSOCIATION_PREFERENCES,
                OglPreferences.SECTION_DEBUG:            OglPreferences.DEBUG_PREFERENCES,
            }
            # loop through each section dictionary
            for sectionName in preferenceSections:
                self.logger.debug(f'{sectionName}')
                preferences: OGL_PREFS_NAME_VALUES = preferenceSections[sectionName]
                self.logger.debug(f'{preferences}')
                # Loop through each preference in the section dictionary
                for preferenceName in preferences:
                    if self._config.has_option(sectionName, preferenceName) is False:
                        value: str = preferences[preferenceName]
                        self._addMissingPreference(sectionName=sectionName, preferenceName=preferenceName, value=value)

        except (ValueError, Exception) as e:
            self.logger.error(f"Error: {e}")

    def _addMissingSections(self):
        for sectionName in OglPreferences.SECTIONS:
            if self._config.has_section(sectionName) is False:
                self._config.add_section(sectionName)

    def _addMissingPreference(self, sectionName: str, preferenceName: str, value: str):
        self._config.set(sectionName, preferenceName, value)
        self._saveConfig()

    def _saveConfig(self):
        """
        Save data to the preferences file
        """
        with open(self._preferencesFileName, "w") as fd:
            self._config.write(fd)
