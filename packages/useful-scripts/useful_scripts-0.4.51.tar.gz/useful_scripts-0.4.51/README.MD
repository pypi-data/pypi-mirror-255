## publish
```bash
Remove-Item -Path 'dist/*' -Recurse -Force
poetry publish --build
```



## test
- **dist/:**
  - [useful_scripts-0.1.0-py3-none-any.whl](dist/useful_scripts-0.1.0-py3-none-any.whl)
  - [useful_scripts-0.1.0.tar.gz](dist/useful_scripts-0.1.0.tar.gz)
  - [useful_scripts-0.1.1-py3-none-any.whl](dist/useful_scripts-0.1.1-py3-none-any.whl)
  - [useful_scripts-0.1.1.tar.gz](dist/useful_scripts-0.1.1.tar.gz)
  - [useful_scripts-0.1.2-py3-none-any.whl](dist/useful_scripts-0.1.2-py3-none-any.whl)
  - [useful_scripts-0.1.2.tar.gz](dist/useful_scripts-0.1.2.tar.gz)
  - [useful_scripts-0.1.3232-py3-none-any.whl](dist/useful_scripts-0.1.3232-py3-none-any.whl)
  - [useful_scripts-0.1.3232.tar.gz](dist/useful_scripts-0.1.3232.tar.gz)
  - [useful_scripts-0.1.332-py3-none-any.whl](dist/useful_scripts-0.1.332-py3-none-any.whl)
  - [useful_scripts-0.1.332.tar.gz](dist/useful_scripts-0.1.332.tar.gz)
- **tests/:**
  - [md_test.py](tests/md_test.py)
- **useful_scripts/:**
  - **docx/:**
    - [code_to-docx.py](useful_scripts/docx/code_to-docx.py)
    - [main.py](useful_scripts/docx/main.py)
  - [main.py](useful_scripts/main.py)
  - **markdown/:**
    - **logs/:**
      - [config.py](useful_scripts/markdown/logs/config.py)
      - [scripts.log](useful_scripts/markdown/logs/scripts.log)
    - [main.py](useful_scripts/markdown/main.py)
    - [obsidian_config_zipper.py](useful_scripts/markdown/obsidian_config_zipper.py)
    - [readme_handler.py](useful_scripts/markdown/readme_handler.py)
  - **paths/:**
    - [main.py](useful_scripts/paths/main.py)
    - [paths.py](useful_scripts/paths/paths.py)
    - [translater.py](useful_scripts/paths/translater.py)
  - **pptx/:**
    - [combine.py](useful_scripts/pptx/combine.py)
    - [main.py](useful_scripts/pptx/main.py)
## test2
### 2024-01-24 by Atticuszz - feat: refactor the cli
- 🔨 [README.MD](README.MD)
- 🔨 [main.py](useful_scripts\markdown\main.py)
- 🔨 [readme_handler.py](useful_scripts\markdown\readme_handler.py)
### 2024-01-24 by Atticuszz - refactor
- 🔨 [README.MD](README.MD)
- 🔨 [poetry.lock](poetry.lock)
- 🔨 [pyproject.toml](pyproject.toml)
- 🗑️ README.md
- 🔨 [md_test.py](tests\md_test.py)
- 🔨 [main.py](useful_scripts\markdown\main.py)
- 🔨 [readme_handler.py](useful_scripts\markdown\readme_handler.py)
- 🔨 [paths.py](useful_scripts\paths\paths.py)
### 2024-01-04 by Atticuszz - add cil and build for package
- 🔨 [README.MD](README.MD)
- 🔨 [scripts.log](useful_scripts\markdown\logs\scripts.log)
- 🔨 [readme_handler.py](useful_scripts\markdown\readme_handler.py)
### 2024-01-04 by Atticuszz - add cil
- ✨ [git_toolbox_prj.xml](.idea\git_toolbox_prj.xml)
- 🔨 [README.MD](README.MD)
- 🗑️ main.py
- 🗑️ scripts.log
- 🔨 [pyproject.toml](pyproject.toml)
- 🔨 [README.md](Invalid path or deleted file)
- 🔨 [md_test.py](tests\md_test.py)
- 🚚 [__init__.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/__init__.py) <- __init__.py
- 🚚 [__init__.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/docx/__init__.py) <- __init__.py
- ✨ [main.py](useful_scripts\docx\main.py)
- ✨ [main.py](useful_scripts\main.py)
- 🚚 [__init__.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/markdown/__init__.py) <- __init__.py
- 🚚 [__init__.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/markdown/logs/__init__.py) <- __init__.py
- 🚚 [config.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/markdown/logs/config.py) <- config.py
- ✨ [scripts.log](useful_scripts\markdown\logs\scripts.log)
- ✨ [main.py](useful_scripts\markdown\main.py)
- 🚚 [obsidian_config_zipper.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/markdown/obsidian_config_zipper.py) <- obsidian_config_zipper.py
- 🚚 [readme_handler.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/markdown/readme_handler.py) <- readme_handler.py
- 🚚 [__init__.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/paths/__init__.py) <- __init__.py
- ✨ [main.py](useful_scripts\paths\main.py)
- 🚚 [paths.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/paths/paths.py) <- paths.py
- 🚚 [translater.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/paths/translater.py) <- translater.py
- ✨ [__init__.py](useful_scripts\pptx\__init__.py)
- 🚚 [combine.py](C:/Users/18317/DevSpace/useful_scripts/useful_scripts/pptx/combine.py) <- combine.py
- ✨ [main.py](useful_scripts\pptx\main.py)
### 2024-01-04 by Atticuszz - reshape md_handler
- ✨ [GitLink.xml](.idea\GitLink.xml)
- 🔨 [misc.xml](.idea\misc.xml)
- 🔨 [ruff.xml](.idea\ruff.xml)
- 🔨 [useful_scripts.iml](.idea\useful_scripts.iml)
- ✨ [README.MD](README.MD)
- 🔨 [readme_handler.py](Invalid path or deleted file)
- 🔨 [paths.py](Invalid path or deleted file)
- 🔨 [poetry.lock](poetry.lock)
- 🔨 [pyproject.toml](pyproject.toml)
- 🔨 [README.md](Invalid path or deleted file)
- 🔨 [md_test.py](tests\md_test.py)
### 2023-12-31 by Atticus Zhou - add markdown handle
- ✨ [__init__.py](Invalid path or deleted file)
- ✨ [code_to_docx.py](Invalid path or deleted file)
- 🔨 [main.py](Invalid path or deleted file)
- ✨ [__init__.py](Invalid path or deleted file)
- ✨ [__init__.py](Invalid path or deleted file)
- ✨ [config.py](Invalid path or deleted file)
- ✨ [scripts.log](Invalid path or deleted file)
- ✨ [obsidian_config_zipper.py](Invalid path or deleted file)
- ✨ [readme_handler.py](Invalid path or deleted file)
- ✨ [paths.py](Invalid path or deleted file)
- 🔨 [poetry.lock](poetry.lock)
- 🔨 [pyproject.toml](pyproject.toml)
- ✨ [README.md](Invalid path or deleted file)
- ✨ [__init__.py](tests\__init__.py)
- ✨ [md_test.py](tests\md_test.py)
### 2023-12-11 by Atticus Zhou - fix pptx combine.py
- 🔨 [poetry.lock](poetry.lock)
- 🗑️ combine.py
- ✨ [combine.py](Invalid path or deleted file)
- 🔨 [pyproject.toml](pyproject.toml)
### 2023-12-11 by Atticus Zhou - add pptx combine.py
- ✨ [.gitignore](.gitignore)
- 🔨 [misc.xml](.idea\misc.xml)
- ✨ [poetry.xml](.idea\poetry.xml)
- ✨ [ruff.xml](.idea\ruff.xml)
- 🔨 [useful_scripts.iml](.idea\useful_scripts.iml)
- ✨ [poetry.lock](poetry.lock)
- ✨ [__init__.py](Invalid path or deleted file)
- ✨ [combine.py](Invalid path or deleted file)
- 🔨 [pyproject.toml](pyproject.toml)
### 2023-10-12 by Atticuszz - initial commit
- ✨ [.gitignore](.idea\.gitignore)
- ✨ [dbnavigator.xml](.idea\dbnavigator.xml)
- ✨ [Project_Default.xml](.idea\inspectionProfiles\Project_Default.xml)
- ✨ [profiles_settings.xml](.idea\inspectionProfiles\profiles_settings.xml)
- ✨ [misc.xml](.idea\misc.xml)
- ✨ [modules.xml](.idea\modules.xml)
- ✨ [useful_scripts.iml](.idea\useful_scripts.iml)
- ✨ [vcs.xml](.idea\vcs.xml)
- ✨ [main.py](Invalid path or deleted file)
- ✨ [__init__.py](Invalid path or deleted file)
- ✨ [translater.py](Invalid path or deleted file)
- ✨ [pyproject.toml](pyproject.toml)
## test3
[test](Invalid path or deleted file)


