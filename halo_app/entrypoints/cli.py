from halo_app import bootstrap
from halo_app.classes import AbsBaseClass
from halo_app.entrypoints.client_type import ClientType
from halo_app.entrypoints import client_util
from halo_app.sys_util import SysUtil

import click

from halo_app.view.query import AbsHaloQuery

c = None

@click.group()
def main():
    """
    Simple CLI for Halo
    """
    global c
    c = Cli()


@main.command()
@click.option("--in", "-i", "usecase_id", required=True,
    help="use case id",
)
@click.option("--params", "-p",
    help="json with parameters")
def command(usecase_id,params):
    """Execute commands on service"""
    global c
    click.echo(usecase_id)
    response = c.run_command(usecase_id,params)

    click.echo(response)

@main.command()
@click.option("--in", "-i", "usecase_id", required=True,
    help="use case id",
)
@click.option("--params", "-p",
    help="json with parameters")
def query(usecase_id,params):
    """Execute queries on service"""
    global c
    click.echo(usecase_id)
    response = c.run_query(usecase_id, params)

    click.echo(response)



class Cli(AbsBaseClass):
    def __init__(self):
        self.boundary = bootstrap.bootstrap()

    def run_command(self,usecase_id,params):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        halo_request = SysUtil.create_command_request(halo_context, usecase_id, params)
        response = self.boundary.execute(halo_request)
        return response.payload

    def run_query(self,usecase_id,params):
        halo_context = client_util.get_halo_context({},client_type=ClientType.cli)
        t = AbsHaloQuery(halo_context,usecase_id, params)
        halo_request = SysUtil.create_query_request(t)
        response = self.boundary.execute(halo_request)
        return response.payload

if __name__ == "__main__":
    main()
