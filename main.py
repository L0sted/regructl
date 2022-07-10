#!/usr/bin/python3
import json
import configparser
import requests
import typer
import os
import prettytable

app = typer.Typer()
server_app = typer.Typer()
app.add_typer(server_app, name='server')
info_submenu = typer.Typer()
app.add_typer(info_submenu, name='info')


class Servers:
    @staticmethod
    def list():
        response = requests.get("https://api.cloudvps.reg.ru/v1/reglets", headers=reqHeader)
        return response.json()

    @staticmethod
    def get_systems():
        response = requests.get("https://api.cloudvps.reg.ru/v1/images?type=distribution", headers=reqHeader)
        return response.json()

    @staticmethod
    def create(name, tariff, image):
        response = requests.post(
            "https://api.cloudvps.reg.ru/v1/reglets",
            headers=reqHeader,
            json={
                "name": name,
                "size": tariff,
                "image": image
            }
        )
        return response.json()

    @staticmethod
    def start(name):
        endpoint = 'https://api.cloudvps.reg.ru/v1/reglets/{id}/actions'
        data = {"type": "start"}
        list_of_servers = Servers.list()
        for i in list_of_servers['reglets']:
            if i['name'] == name:
                result = requests.post(endpoint.format(id=i['id']), headers=reqHeader, json=data)
                return result.json()
        return None

    @staticmethod
    def stop(name):
        endpoint = 'https://api.cloudvps.reg.ru/v1/reglets/{id}/actions'
        data = {"type": "stop"}
        list_of_servers = Servers.list()
        for i in list_of_servers['reglets']:
            if i['name'] == name:
                result = requests.post(endpoint.format(id=i['id']), headers=reqHeader, json=data)
                return result.json()
        return None


def get_balance():
    response = requests.get("https://api.cloudvps.reg.ru/v1/balance_data", headers=reqHeader)
    return response.json()


@info_submenu.command()
def list_plans():
    response = requests.get("https://api.cloudvps.reg.ru/v1/prices", headers=reqHeader)
    print('{0:17} {1:5} {2:5} {3:6}'.format('name', 'hour', 'month', 'unit'))
    for i in response.json()['prices']:
        if i['type'] == 'reglet':
            print('{0:17} {1:5} {2:5} {3:6}'.format(i['plan'], i['price'], i['price_month'], i['unit']))


@info_submenu.command()
def list_os():
    systems_list = Servers.get_systems()['images']
    for i in systems_list:
        print(i['slug'])


@app.command()
def balance():
    print(get_balance())


@server_app.command("list")
def servers_list():
    list_of_servers = Servers.list()
    print('{0:7} {1:17} {2:2} {3:5} {4:4}'.format('state', 'name', 'vcpus', 'memory', 'disk'))
    for i in list_of_servers['reglets']:
        if i['status'] == 'active':
            state = typer.style("Running", fg=typer.colors.GREEN)
        else:
            state = typer.style('Stopped', fg=typer.colors.RED)
        print('{0:15} {1:20} {2:2} {3:5} {4:4}'.format(state, i['name'], i['vcpus'], i['memory'], i['disk']))


@server_app.command("create")
def servers_create(name: str = typer.Option(...), tariff: str = typer.Option(...), image: str = typer.Option(...)):
    print(Servers.create(name=name, tariff=tariff, image=image))


@server_app.command("stop")
def servers_stop(name: str = typer.Option(...)):
    print(Servers.stop(name=name))


def get_api_key():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.getenv('HOME'), '.config', 'regructl.ini'))
    result = config.get('api', 'key', fallback=None)
    if result is None:
        result = input("Enter API Key ")
        config.add_section('api')
        config.set('api', 'key', result)

        with open(os.path.join(os.getenv('HOME'), '.config', 'regructl.ini'), 'w') as configfile:
            config.write(configfile)

    return result


if __name__ == '__main__':
    apikey = get_api_key()
    reqHeader = {"Authorization": "Bearer " + apikey}

    app()
