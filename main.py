#!/usr/bin/python3
import json
import configparser
import requests
import typer
import os

app = typer.Typer()


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
        response = requests.post("https://api.cloudvps.reg.ru/v1/reglets",
                                 headers=reqHeader,
                                 json={"name": name,
                                       "size": tariff,
                                       "image": image
                                       }
                                 )
        return response.json()


def get_balance():
    response = requests.get("https://api.cloudvps.reg.ru/v1/balance_data", headers=reqHeader)
    return response.json()


@app.command()
def get_tariffs():
    response = requests.get("https://api.cloudvps.reg.ru/v1/prices", headers=reqHeader)
    print(json.dumps(response.json(),indent=4))


@app.command()
def balance():
    print(get_balance())


@app.command()
def list_servers():
    list_of_servers = Servers.list()
    print('{0:7} {1:17} {2:2} {3:5} {4:4}'.format('state', 'name', 'vcpus', 'memory', 'disk'))
    for i in list_of_servers['reglets']:
        if i['status'] == 'active':
            state = typer.style("Running", fg=typer.colors.GREEN)
        else:
            state = typer.style('Stopped', fg=typer.colors.RED)
        print('{0:15} {1:20} {2:2} {3:5} {4:4}'.format(state, i['name'], i['vcpus'], i['memory'], i['disk']))


@app.command()
def list_os():
    systems_list = Servers.get_systems()['images']
    for i in systems_list:
        print(i['slug'])


@app.command()
def create_server(name: str = typer.Option(...), tariff: str = typer.Option(...), image: str = typer.Option(...)):
    print(Servers.create(name=name, tariff=tariff, image=image))


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
