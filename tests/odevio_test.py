import inspect
import re
from click.testing import CliRunner
from rich.tree import Tree
from rich.console import Console
from rich.table import Table
from io import StringIO


class OdevioTest:
    command = None

    def __init__(self):
        self.runner = CliRunner()

    def _get_args(self, **args):
        return args

    def _get_output(self, args):
        test = self.__class__.__name__+"."+inspect.stack()[2].function
        print(test, end="...\r", flush=True)
        print(test, end="  ", flush=False)
        result = self.runner.invoke(self.command, self._get_args(**args))
        ansi_remover = re.compile(r'\x1B\[\d+(;\d+)*m')
        return ansi_remover.sub("", result.output)

    def test(self, expected, **args):
        output = self._get_output(args)
        if output != self._console_output(expected):
            raise OdevioTestFailed(expected, output)
        print("\u001b[32mOK\u001b[0m")
        return output

    def test_contains(self, expected, **args):
        output = self._get_output(args)
        output = output.replace("\n", " ").replace("  ", " ")  # Sometimes a newline is inserted, sometimes a space is replaced by a newline...
        if type(expected) is not list:
            expected = [expected]
        for e in expected:
            if e not in output:
                raise OdevioTestFailed(e, output)
        print("\u001b[32mOK\u001b[0m")
        return output

    def test_tree(self, expected, **args):
        output = self._get_output(args)

        def _add_to_tree(tree, children):
            for child in children:
                if type(child) is tuple:
                    branch = tree.add(child[0])
                    _add_to_tree(branch, child[1])
                else:
                    tree.add(child)
        tree = Tree(expected[0])
        _add_to_tree(tree, expected[1])
        expected = self._console_output(tree)
        if output != expected:
            raise OdevioTestFailed(expected, output)
        print("\u001b[32mOK\u001b[0m")

    def _console_output(self, out):
        console = Console(file=StringIO())
        with console.capture() as capture:
            console.print(out)
        return capture.get()

    def test_table(self, expected_columns, expected_rows, expected_title=None, contains=False, **args):
        output = self._get_output(args)
        table = Table(title=expected_title)
        for column in expected_columns:
            table.add_column(column)
        for row in expected_rows:
            table.add_row(*row)
        expected = self._console_output(table)
        if contains and expected not in output or not contains and output != expected:
            raise OdevioTestFailed(expected, output)
        print("\u001b[32mOK\u001b[0m")


class OdevioTestFailed(Exception):
    def __init__(self, expected, output):
        self.expected = expected
        self.output = output

    def __str__(self):
        return f"\u001b[31mFailed\u001b[0m\n\nExpected:\n\u001b[48;5;28m{self.expected}\u001b[0m\nGot:\n\u001b[48;5;88m{self.output}\u001b[0m\n"
