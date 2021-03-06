# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################



class VerdiCommand(object):
    """
    This command has no documentation yet.
    """

    class __metaclass__(type):
        """
        Some python black magic to set correctly the logger also in subclasses.
        """

        def __new__(cls, name, bases, attrs):
            newcls = type.__new__(cls, name, bases, attrs)

            # If the '_abstract' attribute is not explicitly defined in the
            # given class, set it to False.
            if '_abstract' not in attrs:
                newcls._abstract = False

            return newcls

    # This is an abstract class
    _abstract = True

    # To be defined if you want that the name is not generated by the class
    # name, but from a given string
    _custom_command_name = None

    def get_full_command_name(self, with_exec_name=True):
        """
        Return the current command name. Also tries to get the subcommand name.

        :param with_exec_name: if True, return the full string, including the
          executable name ('verdi'). If False, omit it.
        """
        from aiida.cmdline import execname

        subcommand_str = ""

        if with_exec_name:
            exec_name_part = "{} ".format(execname)
        else:
            exec_name_part = ""
        return "{}{}".format(exec_name_part, self.get_command_name())

    @classmethod
    def get_command_name(cls):
        """
        Return the name of the verdi command associated to this
        class. By default, the lower-case version of the class name.
        """
        if cls._custom_command_name is None:
            return cls.__name__.lower()
        else:
            return cls._custom_command_name

    def run(self, *args):
        """
        Method executed when the command is called from the command line.
        """
        import sys

        print >> sys.stderr, "This command has not been implemented yet"

    def complete(self, subargs_idx, subargs):
        """
        Method called when the user asks for the bash completion.
        Print a list of valid keywords.
        Returning without printing will use standard bash completion.

        :param subargs_idx: the index of the subargs where the TAB key was pressed\
            (0 is the first element of subargs)
        :param subargs: a list of subarguments to this command
        """
        return


class VerdiCommandRouter(VerdiCommand):
    _abstract = True

    # Empty valid subcommands to start with;
    # These should be a dictionary with 'key' the name to type on the
    # command line, and value a VerdiCommand class to call when that subcommand
    # is invoked.
    routed_subcommands = {}

    def no_subcommand(self, *args):
        import sys

        if self.routed_subcommands:
            print >> sys.stderr, ("You have to pass a valid subcommand to "
                                  "{}.\nValid subcommands are:".format(
                self.get_full_command_name()))
            print >> sys.stderr, "\n".join("  {}".format(sc)
                                           for sc in self.routed_subcommands)
        else:
            print >> sys.stderr, ("There are no valid subcommand to "
                                  "{}.".format(self.get_full_command_name()))
        sys.exit(1)

    def invalid_subcommand(self, *args):
        import sys

        if self.routed_subcommands:
            print >> sys.stderr, ("You passed an invalid subcommand to '{}'.\n"
                                  "Valid subcommands are:".format(
                self.get_full_command_name()))
            print >> sys.stderr, "\n".join("  {}".format(sc)
                                           for sc in self.routed_subcommands)
        else:
            print >> sys.stderr, ("There are no valid subcommand to "
                                  "{}.".format(self.get_full_command_name()))
        sys.exit(1)

    def run(self, *args):
        try:
            the_class = self.routed_subcommands[args[0]]
            the_class._custom_command_name = "{} {}".format(
                self.get_full_command_name(with_exec_name=False), args[0])
            function_to_call = the_class().run
        except IndexError:
            function_to_call = self.no_subcommand
        except KeyError:
            function_to_call = self.invalid_subcommand

        function_to_call(*args[1:])

    def complete(self, subargs_idx, subargs):
        if subargs_idx == 0:
            print "\n".join(self.routed_subcommands.keys())
        elif subargs_idx >= 1:
            try:
                first_subarg = subargs[0]
            except  IndexError:
                first_subarg = ''

            try:
                complete_function = self.routed_subcommands[
                    first_subarg]().complete
            except KeyError:
                print ""
                return
            complete_function(subargs_idx - 1, subargs[1:])


class VerdiCommandWithSubcommands(VerdiCommand):
    """
    Used for commands with subcommands. Just define, in the __init__,
    the self.valid_subcommands dictionary, in the format::

     self.valid_subcommands = {
         'uploadfamily': (self.uploadfamily, self.complete_auto),
         'listfamilies': (self.listfamilies, self.complete_none),
         }

    where the key is the subcommand name to give on the command line, and
    the value is a tuple of length 2, the first is the function to call on
    execution, the second is the function to call on complete.

    This class already defined the complete_auto and complete_none commands,
    that respectively call the default bash completion for filenames/folders,
    or do not give any completion suggestion.
    Other functions can of course be defined.

    .. todo:: Improve the docstrings for commands with subcommands.
    """
    _abstract = True

    valid_subcommands = {}

    def run(self, *args):
        try:
            function_to_call = self.valid_subcommands[args[0]][0]
        except IndexError:
            function_to_call = self.no_subcommand
        except KeyError:
            function_to_call = self.invalid_subcommand

        function_to_call(*args[1:])

    def complete(self, subargs_idx, subargs):
        if subargs_idx == 0:
            print "\n".join(self.valid_subcommands.keys())
        elif subargs_idx >= 1:
            try:
                first_subarg = subargs[0]
            except IndexError:
                first_subarg = ''
            try:
                complete_function = self.valid_subcommands[first_subarg][1]
            except KeyError:
                print ""
                return
            complete_data = complete_function(subargs_idx - 1, subargs[1:])
            if complete_data is not None:
                print complete_data

    def complete_none(self, subargs_idx, subargs):
        return ""

    def complete_auto(self, subargs_idx, subargs):
        return None

    def no_subcommand(self, *args):
        import sys

        if self.valid_subcommands:
            print >> sys.stderr, ("You have to pass a valid subcommand to "
                                  "'{}'.\nValid subcommands are:".format(
                self.get_full_command_name()))
            print >> sys.stderr, "\n".join("  {}".format(sc)
                                           for sc in self.valid_subcommands)
        else:
            print >> sys.stderr, ("There are no valid subcommands to "
                                  "'{}'.".format(self.get_full_command_name()))
        sys.exit(1)

    def invalid_subcommand(self, *args):
        import sys

        if self.valid_subcommands:
            print >> sys.stderr, ("You passed an invalid subcommand to '{}'.\n"
                                  "Valid subcommands are:".format(
                self.get_full_command_name()))
            print >> sys.stderr, "\n".join("  {}".format(sc)
                                           for sc in self.valid_subcommands)
        else:
            print >> sys.stderr, ("There are no valid subcommands to "
                                  "'{}'.".format(self.get_full_command_name()))

        sys.exit(1)

    def get_full_command_name(self, *args, **kwargs):
        """
        Return the current command name. Also tries to get the subcommand name.

        Also tries to see if the caller function was one specific submethod.

        :param with_exec_name: if True, return the full string, including the
          executable name ('verdi'). If False, omit it.
        """
        import inspect

        from aiida.cmdline import execname

        subcommand_str = ""

        try:
            # [0]: this function;
            # [1]: function that directly called this function
            # So I go in order from the function that called to the above
            # function, etc. until I find it, if I can
            found = False
            for caller_function in inspect.stack()[1:]:
                if found == True:
                    break
                for k, v in self.valid_subcommands.iteritems():
                    if v[0].__name__ == caller_function[3]:
                        subcommand_str = " {}".format(k)
                        found = True
                        break
        except (KeyError, AttributeError, IndexError):
            # Some of this info could not be retrived, do not set
            # the subcommand name
            pass

        return "{}{}".format(
            super(VerdiCommandWithSubcommands, self).get_full_command_name(
                *args, **kwargs),
            subcommand_str)
