from ...core.analyzer.advanced_consumer import MethodStruct, ClassStruct

# https://www.oracle.com/technical-resources/articles/java/javadoc-tool.html
class JavadocStruct:
    def __init__(self):
        self._see = None        # @see
        self._params = None     # @param (methods and constructors only)
        self._return = None     # @return (methods only)
        self._throws = None     # @throws | @exception
        self._serials = None    # @serial (or @serialField or @serialData)

class StructuresResolver:
    pass
