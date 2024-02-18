import warnings


class insertokname-authlibDeprecationWarning(DeprecationWarning):
    pass


warnings.simplefilter('always', insertokname-authlibDeprecationWarning)


def deprecate(message, version=None, link_uid=None, link_file=None):
    if version:
        message += f'\nIt will be compatible before version {version}.'
    if link_uid and link_file:
        message += f'\nRead more <https://git.io/{link_uid}#file-{link_file}-md>'
    warnings.warn(insertokname-authlibDeprecationWarning(message), stacklevel=2)
