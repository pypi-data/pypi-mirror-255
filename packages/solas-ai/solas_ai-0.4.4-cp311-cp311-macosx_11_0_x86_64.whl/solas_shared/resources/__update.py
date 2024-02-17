"""This is a private, internal-use, maintenance script to update embedded
resources from primary sources."""
from pathlib import Path

import requests

resources = [
    ["https://fonts.googleapis.com/icon?family=Material+Icons", "material.icons.css"],
    [
        "https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css",
        "materialize.min.css",
    ],
    [
        "https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js",
        "materialize.min.js",
    ],
    ["https://polyfill.io/v3/polyfill.min.js?features=es6", "polyfill.min.js"],
    ["https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js", "tex-mml-chtml.js"],
]


def update_resources():
    for rsrc in resources:
        r = requests.get(rsrc[0])
        with open(Path(__file__).parent / rsrc[1], "w") as f:
            f.write(r.text)


if __name__ == "__main__":
    update_resources()
