class EmbloySession:
    """
    A class used to represent a session for the Embloy API.

    Attributes
    ----------
    mode : str
        The mode of the session.
    job_slug : str
        The job slug for the session.
    success_url : str
        The success URL for the session.
    cancel_url : str
        The cancel URL for the session.

    Methods
    -------
    __init__(mode, job_slug, success_url, cancel_url)
        Initializes the EmbloySession.
    """

class SessionOptions:
    def __init__(self, success_url=None, cancel_url=None, **kwargs):
        self.success_url = success_url
        self.cancel_url = cancel_url
        self.__dict__.update(kwargs)

class EmbloySession:
    def __init__(self, mode, job_slug, options=SessionOptions()):
        """
        Initializes the EmbloySession.

        Parameters
        ----------
        mode : str
            The mode of the session.
        job_slug : str
            The job slug for the session.
        success_url : str, optional
            The success URL for the session.
        cancel_url : str, optional
            The cancel URL for the session.
        """
        if not mode:
            raise ValueError("mode is required")
        if not job_slug:
            raise ValueError("job_slug is required")

        self.mode = mode
        self.job_slug = job_slug
        self.success_url = options.success_url
        self.cancel_url = options.cancel_url
