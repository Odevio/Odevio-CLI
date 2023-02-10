import click

from appollo.helpers import login_required_warning_decorator

@click.command()
@login_required_warning_decorator
@click.option('--extra-test-paramters', help="option to add personal option")
def test(extra_test_paramters):