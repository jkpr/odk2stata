class VarnameManager:

    def __init__(self):
        pass

    def get_temp_v2_varname(self, varname: str) -> str:
        """Get a temporary v2 varname.

        This is used when generating a new varname that is used for only a
        little while.

        Args:
            varname: A Stata varname

        Returns:
            The varname to be used as a temporary varname
        """
        varname_stem = varname[:30]
        new_varname = f'{varname_stem}V2'
        return new_varname

    def get_label_varname(self, choice_list_name: str) -> str:
        """Take input choice list name and return Stata varname.

        A choice list name might not be a valid Stata identifier. This
        method returns a valid Stata identifier.

        Args:
            choice_list_name: The name of the choice list

        Returns:
            A Stata varname that is used for a "label define" command
        """
        new_varname = choice_list_name[:32]
        return new_varname
