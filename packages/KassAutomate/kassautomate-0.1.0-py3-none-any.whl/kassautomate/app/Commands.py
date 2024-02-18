import os
from pathlib import Path

import click
from KassOrm import Migration, Modelr

from kassautomate.app.Console import console as dd


class Commands:
    def __init__(self, app) -> None:
        """Classe responsavel por gerenciar os comandos internos

        Args:
            app (flask): aplicação Flask
        """
        self.app = app

        self.commands()

    def init(self):
        """Retorna o flask com os comnados iniciados

        Returns:
            flask: aplicação em flask
        """
        return self.app

    def commands(self):
        """Todos os comandos internos criados"""

        @self.app.cli.command("make:controller")
        @click.argument("pathcontroller")
        def controller(pathcontroller: str):
            pathControllers = "app/controllers"

            name = pathcontroller.rsplit("/")[-1]
            pathcontroller = Path(
                pathControllers + "/" + pathcontroller.replace(f"/{name}", "")
            )
            name = name.lower().capitalize().replace("controller", "") + "Controller"

            if not os.path.exists(pathcontroller):
                os.makedirs(pathcontroller)

            stub = open(f"core/stubs/controller.stub", "r+")
            stub_content = stub.read()
            stub.close()

            stub_content = stub_content.replace("%CLASSNAME%", name)
            filePath = f"{pathcontroller}/{name}.py"

            if os.path.exists(filePath):
                dd(f"Controller '{filePath}' already exists").danger()
                return

            id = 1  # Job().insert({"name": name, "active": 1})

            stub_content = stub_content.replace("%ID%", str(id))

            controller_file = open(filePath, "w+")
            controller_file.writelines(stub_content)
            controller_file.close()

            dd(f"Controller '{filePath}' successfully created").success()

        @self.app.cli.command("make:model")
        @click.argument("tablename")
        @click.option("-c", "--comment")
        def createModel(tablename: str, comment: str = ""):
            """Cria um modelo dentro do modulo especificado

            Args:
                pathmodule (str):  caminho ate o nome do modulo
                tablename (str): nome da tabela no banco de dados
                comment (str, optional): comentario sobre o model. Defaults to "".
            """

            pathModels = f"app/database/models"
            comment = "" if comment == None else comment
            result = Modelr().make_file_model(pathModels, tablename, comment)

            if result == True:
                dd(f"\n{tablename.capitalize()} - Model successfully created").success()
            else:
                dd(f"f'\n{tablename.capitalize()} - Model not created").danger()
                dd(result).danger()

        @self.app.cli.command("make:migration")
        @click.argument("migration_name")
        @click.option("-c", "--comment")
        @click.option("-c", "--model")
        def createMigration(migration_name: str, comment: str = "", model: str = None):
            """Cria uma migration dentro do módulo especificado

            Args:
                pathmodule (str):  caminho ate o nome do modulo
                migration_name (str): nome da migration (use os prefixos 'create_' e 'alter_')
                tablename (str): nome da tabela no banco de dados
                comment (str, optional): comentario sobre o uso dessa migration. Defaults to "".
            """

            pathModels = f"app/database/models"
            pathMigrations = f"app/database/migrations"
            tablename = migration_name.rsplit("_")[-1]
            comment = "" if comment == None else comment

            Migration().make_file_migration(
                migration_name, pathMigrations, tablename, comment
            )
            dd(f"\n{migration_name} - Migration successfully created").success()

            if model != None:
                result = Modelr().make_file_model(pathModels, tablename, comment)
                if result == True:
                    dd(
                        f"\n{tablename.capitalize()} - Model successfully created"
                    ).success()
                else:
                    dd(f"f'\n{tablename.capitalize()} - Model not created").danger()
                    dd(result).danger()

        @self.app.cli.command("migrate")
        def runMigrations():
            """Executa as migrations dentro do módulo especificado

            Args:
                pathmodule (str):  caminho ate o nome do modulo
            """

            dir_migration = f"app/database/migrations"
            conn = None

            Migration(conn=conn).migrate(dir_migration)
            dd(f"\nMigrations successfully executed").success()

        @self.app.cli.command("migrate:fresh")
        def freshRunMigrations():
            """Deleta todo o banco de dados e executa do zero as migrations dentro do módulo especificado

            Args:
                pathmodule (str):  caminho ate o nome do modulo
            """

            envs = ["development"]
            if os.getenv("ENV") not in ["development"]:
                dd(f"\n[COMANDO SOMENTE EM {envs}!]").danger()
                return

            dir_migration = f"app/database/migrations"
            conn = None

            Migration(conn=conn).drop_all_migrations(dir_migration)
            Migration(conn=conn).migrate(dir_migration)
            dd(f"\nMigrations successfully executed").success().save(
                title="comando migrate:fresh"
            )
