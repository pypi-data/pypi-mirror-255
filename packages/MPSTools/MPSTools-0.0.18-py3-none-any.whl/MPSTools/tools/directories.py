#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import MPSTools


__all__ = [
    'root_path',
    'project_path',
    'example_directory',
    'doc_path',
    'doc_css_path',
    'logo_path',
    'version_path',
]

root_path = Path(MPSTools.__path__[0])

project_path = root_path.parents[0]

doc_path = root_path.parents[0].joinpath('docs')

example_directory = doc_path.joinpath('examples')

doc_css_path = doc_path.joinpath('source/_static/default.css')

fonts_directory = root_path.joinpath('fonts')

logo_path = doc_path.joinpath('images/logo.png')

version_path = root_path.joinpath('VERSION')


if __name__ == '__main__':
    for path_name in __all__:
        path = locals()[path_name]
        print(path)
        assert path.exists(), f"Path {path_name} do not exists"

# -
