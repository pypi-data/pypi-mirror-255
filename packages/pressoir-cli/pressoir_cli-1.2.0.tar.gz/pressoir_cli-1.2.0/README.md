# Pressoir CLI

## Installation

Pré-requis : Python3.8+

Installer et activer un environnement virtuel :

    $ python3 -m venv venv
    $ source venv/bin/activate

Installer les dépendances :

    $ make install

## Initialiser un livre

Par exemple :

    $ pressoir-cli init --repository-path=../fia --collection sp

ou

    $ pressoir-cli init --repository-path=../12-editionscritiques --collection pum

Note : si la destination n’existe pas ou n’a pas de dossier `textes`,
une coquille complète du livre est créée.

## Construire un livre

    $ pressoir-cli build --repository-path=../fia-en

Avec `../fia-en` qui est le chemin vers le dépôt du livre.

En bonus, il est possible de passer un chapitre particulier pour ne reconstruire que lui :

    $ pressoir-cli build --repository-path=../fia-en --chapter=chapter1

## Servir un livre

    $ pressoir-cli serve --repository-path=../fia-en

Avec `../fia-en` qui est le chemin vers le dépôt du livre qui a été construit.


## Help

### Commands

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir-cli --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir-cli [-h]  ...

options:
  -h, --help  Show this help message and exit

Available commands:
  
    init      Initialize a new book to `repository_path` or current directory.
    build     Build a book from `repository_path` or current directory.
    serve     Serve an HTML book from `repository_path`/public or current
              directory/public.

```
<!-- [[[end]]] -->

### Command: `init`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir-cli init --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir-cli init [-h] [--repository-path REPOSITORY_PATH]
                         [--collection {pum,sp}]

options:
  -h, --help            show this help message and exit
  --repository-path REPOSITORY_PATH
                        Absolute or relative path to book’s sources (default:
                        current).
  --collection {pum,sp}, -c {pum,sp}
                        Name of the collection (Presses Universitaires or
                        Sens-Public).

```
<!-- [[[end]]] -->


### Command: `build`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir-cli build --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir-cli build [-h] [--repository-path REPOSITORY_PATH]
                          [--target-path TARGET_PATH] [--chapter CHAPTER]

options:
  -h, --help            show this help message and exit
  --repository-path REPOSITORY_PATH
                        Absolute or relative path to book’s sources (default:
                        current).
  --target-path TARGET_PATH
                        Where the book will be built (default:
                        `repository_path`/public).
  --chapter CHAPTER, -c CHAPTER
                        Specify a given chapter id (e.g. `chapter1`).

```
<!-- [[[end]]] -->


### Command: `serve`

<!-- [[[cog
import subprocess
import cog
output = subprocess.check_output("pressoir-cli serve --help", shell=True)
help = output.decode().split("\n", 1)[1]  # Remove Pandoc version.
cog.out(f"```\n{help}\n```")
]]] -->
```
usage: pressoir-cli serve [-h] [--repository-path REPOSITORY_PATH]
                          [--port PORT]

options:
  -h, --help            show this help message and exit
  --repository-path REPOSITORY_PATH
                        Absolute or relative path to book’s sources (default:
                        current).
  --port PORT, -p PORT  Port to serve the book from (default=8000)

```
<!-- [[[end]]] -->
