
from logging import Logger
from logging import getLogger

from codeallybasic.SingletonV3 import SingletonV3

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType

from ogl.OglAssociation import OglAssociation
from ogl.OglAggregation import OglAggregation
from ogl.OglComposition import OglComposition
from ogl.OglInheritance import OglInheritance
from ogl.OglInterface import OglInterface
from ogl.OglNoteLink import OglNoteLink

from ogl.sd.OglSDMessage import OglSDMessage


def getOglLinkFactory():
    """
    Function to get the unique OglLinkFactory instance (singleton).
    """
    return OglLinkFactory()


def getLinkType(link: OglAssociation) -> PyutLinkType:
    """

    Args:
        link:   The enumeration OglLinkType

    Returns:  The OglLinkType

    """

    if isinstance(link, OglAggregation):
        return PyutLinkType.AGGREGATION
    elif isinstance(link, OglComposition):
        return PyutLinkType.COMPOSITION
    elif isinstance(link, OglInheritance):
        return PyutLinkType.INHERITANCE
    elif isinstance(link, OglAssociation):
        return PyutLinkType.ASSOCIATION
    elif isinstance(link, OglInterface):
        return PyutLinkType.INTERFACE
    elif isinstance(link, OglNoteLink):
        return PyutLinkType.NOTELINK


class OglLinkFactory(metaclass=SingletonV3):
    """
    This class is a factory to produce `OglLink` objects.
    It works under the Factory Design Pattern model. Ask for a link
    from this object, and it will return an instance of request link.
    """
    def __init__(self):

        self.logger: Logger = getLogger(__name__)

    def getOglLink(self, srcShape, pyutLink, destShape, linkType: PyutLinkType):
        """
        Used to get an OglLink of the given linkType.

        Args:
            srcShape:   Source shape
            pyutLink:   Conceptual links associated with the graphical links.
            destShape:  Destination shape
            linkType:   The linkType of the link (OGL_INHERITANCE, ...)

        Returns:  The requested link
        """
        if linkType == PyutLinkType.AGGREGATION:
            return OglAggregation(srcShape, pyutLink, destShape)

        elif linkType == PyutLinkType.COMPOSITION:
            return OglComposition(srcShape, pyutLink, destShape)

        elif linkType == PyutLinkType.INHERITANCE:
            return OglInheritance(srcShape, pyutLink, destShape)

        elif linkType == PyutLinkType.ASSOCIATION:
            return OglAssociation(srcShape, pyutLink, destShape)

        elif linkType == PyutLinkType.INTERFACE:
            return OglInterface(srcShape, pyutLink, destShape)

        elif linkType == PyutLinkType.NOTELINK:
            return OglNoteLink(srcShape, pyutLink, destShape)

        elif linkType == PyutLinkType.SD_MESSAGE:
            return OglSDMessage(srcSDInstance=srcShape, pyutSDMessage=pyutLink, dstSDInstance=destShape)
        else:
            self.logger.error(f"Unknown OglLinkType: {linkType}")
            return None
