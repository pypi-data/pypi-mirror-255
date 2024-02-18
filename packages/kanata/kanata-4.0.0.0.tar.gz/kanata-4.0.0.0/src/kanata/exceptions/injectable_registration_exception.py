class InjectableRegistrationException(Exception):
    """Raised when registering an injectable fails."""

    def __init__(
        self,
        related_type: type | None = None,
        message: str | None = None
    ) -> None:
        """Initializes a new instance.

        :param related_type: An optional type related to the exception, defaults to None.
        :type related_type: type, optional
        :param message: An optional message that describes the problem, defaults to None.
        :type message: str, optional
        """

        super().__init__(message)
        self.__related_type = related_type

    @property
    def related_type(self) -> type | None:
        """Gets the type related to the exception.

        :return: The type related to the exception.
        :rtype: type | None
        """

        return self.__related_type
