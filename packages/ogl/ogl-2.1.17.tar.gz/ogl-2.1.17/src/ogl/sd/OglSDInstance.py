
from typing import cast

from logging import Logger
from logging import getLogger

from deprecated import deprecated

from wx import BLACK_DASHED_PEN
from wx import PENSTYLE_LONG_DASH

from wx import Colour
from wx import Pen

from pyutmodelv2.PyutSDInstance import PyutSDInstance

from miniogl.AnchorPoint import AnchorPoint
from miniogl.LineShape import LineShape
from miniogl.RectangleShape import RectangleShape

from ogl.OglObject import OglObject
from ogl.preferences.OglPreferences import OglPreferences

from ogl.sd.OglInstanceName import OglInstanceName


class OglSDInstance(OglObject):
    """
    Class Diagram Instance
    This class is an OGL object for class diagram instance (vertical line)
    """

    def __init__(self, pyutObject: PyutSDInstance):
        """
        """
        self.logger:       Logger         = getLogger(__name__)

        prefs: OglPreferences = OglPreferences()    # need our own since superclass constructs it
        super().__init__(pyutObject, prefs.instanceDimensions.width, prefs.instanceDimensions.height)

        self._instanceYPosition: int = self._prefs.instanceYPosition  # User super class version

        self.draggable = True
        self.SetVisible(True)
        self.SetPen(Pen(Colour(200, 200, 255), 1, PENSTYLE_LONG_DASH))
        self.SetPosition(self.GetPosition()[0], self._instanceYPosition)

        self._lifeLine:     LineShape       = self._createLifeLine()
        self._instance:     RectangleShape  = self._createInstance()
        self._instanceName: OglInstanceName = self._createInstanceName(pyutSDInstance=pyutObject, instanceBox=self._instance)
        # TODO : set instance box size to the size of the text by invoking self._instanceBoxText.setSize()

    @deprecated(reason="Use the property '.lifeline'")
    def getLifeLineShape(self):
        """
        Used by OGLSDMessage to use it as parent

        Returns: The lifeline object
        """
        return self._lifeLine

    @property
    def lifeline(self) -> LineShape:
        """
        Used by OGLSDMessage to use it as parent and

        Returns: The lifeline object
        """
        return self._lifeLine

    @property
    def instance(self) -> RectangleShape:
        return self._instance

    @property
    def instanceName(self) -> OglInstanceName:
        return self._instanceName

    def OnInstanceBoxResize(self, sizer, width: int, height: int):
        """
        Resize the instance box, so all instance

        Args:
            sizer:
            width:
            height:

        """
        """

        @param double x, y : position of the sizer
        """
        RectangleShape.Resize(self._instance, sizer, width, height)
        size = self._instance.GetSize()
        self.SetSize(size[0], self.GetSize()[1])

    def Resize(self, sizer, width: int, height: int):
        """
        Resize the rectangle according to the new position of the sizer.

        Args:
            sizer:
            width:
            height:
        """
        OglObject.Resize(self, sizer, width, height)

    def SetSize(self, width: int, height: int):
        """
        """
        OglObject.SetSize(self, width, height)
        # Set lifeline
        (myX, myY) = self.GetPosition()
        (w, h) = self.GetSize()
        lineDst = self._lifeLine.destinationAnchor
        lineSrc = self._lifeLine.sourceAnchor
        lineSrc.draggable = True
        lineDst.draggable = True
        lineSrc.SetPosition(w // 2 + myX, 0 + myY)
        lineDst.SetPosition(w // 2 + myX, height + myY)
        lineSrc.draggable = False
        lineDst.draggable = False

        from ogl.sd.OglSDMessage import OglSDMessage
        # Update all OglSDMessage positions
        for link in self._oglLinks:
            try:
                oglSDMessage: OglSDMessage = cast(OglSDMessage, link)
                oglSDMessage.updatePositions()
            except (ValueError, Exception) as e:
                self.logger.error(f'Link update position error: {e}')
        # Set TextBox
        RectangleShape.SetSize(self._instance, width, self._instance.GetSize()[1])

    def SetPosition(self, x: int, y: int):
        """
        Debug
        """
        y = self._instanceYPosition
        OglObject.SetPosition(self, x, y)

    def Draw(self, dc, withChildren=True):
        """
        Draw override
        Args:
            dc:
            withChildren:  defaulted to True because of the child shapes
        """
        # Update labels
        self._instanceName.text = self._pyutObject.instanceName
        # Call parent's Draw method
        if self.selected is True:
            self.SetVisible(True)
            self.SetPen(Pen(Colour(200, 200, 255), 1, PENSTYLE_LONG_DASH))

        super().Draw(dc=dc, withChildren=withChildren)

    def OnLeftUp(self, event):
        """
        Callback for left clicks.
        """
        self.SetPosition(self.GetPosition()[0], self._instanceYPosition)

    def _createLifeLine(self) -> LineShape:
        """

        Returns:  The lifeline
        """
        width:   int = self._prefs.instanceDimensions.width
        height: int  = self._prefs.instanceDimensions.height
        (srcX, srcY, dstX, dstY) = (width // 2, 0,
                                    width // 2, height
                                    )

        (src, dst) = (AnchorPoint(srcX, srcY, self), AnchorPoint(dstX, dstY, self))
        for el in [src, dst]:
            el.SetVisible(False)
            el.draggable = False

        lifeLineShape: LineShape = LineShape(src, dst)

        lifeLineShape.SetParent(self)
        lifeLineShape.SetDrawArrow(False)
        lifeLineShape.draggable = True
        lifeLineShape.SetPen(BLACK_DASHED_PEN)
        lifeLineShape.SetVisible(True)

        self.AppendChild(lifeLineShape)

        return lifeLineShape

    def _createInstance(self) -> RectangleShape:
        """

        Returns:  The instance box
        """
        instanceBox: RectangleShape = RectangleShape(0, 0, 100, 50)

        instanceBox.draggable = False
        instanceBox.Resize = self.OnInstanceBoxResize   # type: ignore
        instanceBox.SetResizable(True)
        instanceBox.SetParent(self)

        self.AppendChild(instanceBox)

        return instanceBox

    def _createInstanceName(self, pyutSDInstance: PyutSDInstance, instanceBox: RectangleShape) -> OglInstanceName:
        """

        Returns:  An OglInstanceName
        """
        text: str = self._pyutObject.instanceName

        oglInstanceName: OglInstanceName = OglInstanceName(pyutSDInstance, 0, 20, text, instanceBox)

        self.AppendChild(oglInstanceName)

        return oglInstanceName

    def __str__(self) -> str:
        instanceName: str = self._pyutObject.instanceName
        return f'OglSDInstance[{self._id=} {instanceName=}]'

    def __repr__(self) -> str:
        return self.__str__()
