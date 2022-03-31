class IncorrectFormat(Exception):
    """Exception raised for errors in the input format.

    Attributes:
        `format`(str): input format which caused the error.
        `message`(str): explanation of the error.
    """
    def __init__(self, format, message=
        """This format is incorrect.
        Theses are the avaible ones : "day", "week", "month"."""):
        self.format = format
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return f""""{self.format}" -> {self.message}"""