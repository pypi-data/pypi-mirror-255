# Licere

Generate License files using variables and templates.

- Because copying and pasting is hard.
  - ... Even huge companies fail to enter the details right (e.g. Year/Copyright Owner).

- Because some people need licenses. 
  - ... The entire attorney industrial complex.

- Because licensing should be customizable.
  - ... There is no one size fits all.

# Features

- Jinja Templating
- Template Packages
- Custom Licenses
- Render multiple output types (Text/Markdown/HTML)

# Quick Start

1. Install:

  ```shell
  pip install licere
  ```

2. Generate a license:

  ```
  # generate a polyform strict license
  licere generate --license polyform-strict
  
  # generate an apache license with a proper copyright
  licere generate --license apache copyright_year=2024 copyright_owner="Example Company"
  
  # load data from a file
  licere generate --license apache --data=data.toml
  
  # where data.toml is:
  # copyright_year = "2024" 
  # copyright_owner = "Example Company"
  ```

# Included Licenses

- Polyform
- Apache
- MIT
- BSD