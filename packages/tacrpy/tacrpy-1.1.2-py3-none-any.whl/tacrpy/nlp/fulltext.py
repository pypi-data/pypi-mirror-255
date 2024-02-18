import re


def find_project_code(text: str, prog_select: str | list = None) -> list:
    """ Vyhledá v textu kódy projektů.

    :param text: vstupní text
    :param prog_select: kód programu nebo list kódů programů, jejichž projekty nás specificky zajímají
    :return: list kódů projektů v textu
    """

    projects = re.findall('\w{2}\d{6,8}', text)

    if prog_select is not None:
        if isinstance(prog_select, list):
            projects = [proj for proj in projects if proj[:2] in prog_select]
        elif isinstance(prog_select, str):
            prog_select = [prog_select]
            projects = [proj for proj in projects if proj[:2] in prog_select]

    return projects
