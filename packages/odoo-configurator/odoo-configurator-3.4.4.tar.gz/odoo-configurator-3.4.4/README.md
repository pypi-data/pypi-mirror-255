odoo-configurator
=================

Odoo Configurator simplifies and automates the configuration of Odoo using YAML files. 
It allows you to update the database, install/update/uninstall modules, configure settings, 
manage users, and perform various data manipulation operations. 
It is an essential tool for Odoo administrators looking to streamline their configuration workflow.

## Installation

    pip install odoo-configurator

## Usage

    odoo-configurator ./work_dir/project_name.local.yml

To run a configuration from the source code:

    /odoo-configurator/start_config.py ./work_dir/project_name.local.yml

Provided file must contain the auth/odoo section to set connexion parameters.

#### project_name.local.yml

```yml
    name: project_name local

    inherits:
        - ../work_dir/project_name/project_name.yml

    auth:
        odoo:
            url: http://project_name.localhost
            dbname: project_name
            username: admin
            password: admin123
```

## Inherits

Inherits param provide a list of configuration files witch content is merged before execution.

```yml
    inherits:
        - ../work_dir/project_name/sales.yml
        - ../work_dir/project_name/account.yml
 ```

## Script Files

Script Files param provide a list of configuration files witch content will be executed sequentially.

```yml
    script_files:
        - ../work_dir/project_name/script1.yml
        - ../work_dir/project_name/script2.yml
```

## Parameters

**Install Mode**: To import datas with the value **on_install_only: True** add the "--install" parameter in command
line:

    ./start_config.py ./clients/name/name.local.yml --install

## Environment variables

Some parameters can be provided by environment variable.

Use ODOO_URL, ODOO_DB, ODOO_USER and ODOO_PASSWORD instead of using auth/odoo params in config file

Use KEEPASS_PASSWORD instead of --keepass command line parameter

## Pre Update

To prepare a configuration or add a fix use "pre_update", the given scripts will be executed before the normal configuration.

```yml
    pre_update:
        - ../exemple/exemple.pre_update_script.yml
```

## Modules

To install modules use "modules"
```yml
    base:
      modules:
        - example_module
```

To update modules use "updates"
```yml
    base:
      updates:
        - example_module
```

To uninstall modules use "uninstall_modules"
```yml
    base:
      uninstall_modules:
        - example_module
```

## Set config parameters (Settings)

to set the value of a setting (res.config.settings)
```yml
    settings:
      config:
        group_use_lead: True
```

For a specific company configuration use the `company_id` parameter:
```yml
    settings main_company:
      config:
        company_id: get_ref("base.main_company")
        chart_template_id: get_ref("l10n_fr.l10n_fr_pcg_chart_template")
        context: { 'lang': 'fr_FR' }
```

A context can be passed to the config command.

## Set system parameters

to set the value of a system parameter (ir.config_parameter)
```yml
Company System Parameters:
  system_parameter:
    Mail Default From Filter:
      key: mail.default.from_filter
      value: my-company.com
  ```


## Create or update records
    
If the record with the xml id provided with force_id don't exist, the record will be created.    

```yml
    Records to create:
        datas:
            My record 1:
                model: res.partner
                force_id: external_config.partner_1
                values:
                    name: Partner 1
                    ref: PARTNER1
            My record 2:
                model: res.user
                force_id: base.user_admin
                values:
                    name: Admin User
```

## Load records

Using load parameter will speed up creation and update of record compared to single record update.

```yml
    Records to load:
        load: True
        model: res.partner
        datas:
            My record 1:
                force_id: external_config.record1
                values:
                    name: Record 1
                    ref: REC1
            My record 2:
                force_id: external_config.record2
                values:
                    name: Record 2
                    ref: REC2
```

## Update records with a domain

To update values of multiple records, set a domain with "update_domain" :
```yml
    Update Example:
      model: res.partner
      update_domain: "[('email','=','example@test.com')]"
      values:
        name: Example
```

## Available functions

All functions in OdooConnection starting by `get_` are callable from yml files.
 - get_ref
 - get_image_url
 - get_image_local
 - get_local_file
 - get_country
 - get_menu
 - get_search_id
 - get_xml_id_from_id
 - get_record

These functions can be nested by using the o object:

```yml
Ir model Data Config:
  datas:
    Add employee document xmlid:
      model: ir.model.data
      force_id: template_01_employee_01
      values:
        model: paper.paper
        module: external_config
        name: template_01_employee_01
        res_id: get_search_id('paper.paper', [
                ('template_id', '=', o.get_ref('external_config.template_01')),
                ('res_id', '=', o.get_ref('external_config.employee_01'))
                ], 'desc')
```

## Server Actions and Functions

To call a model function:
```yml
    001 Call Function:
      datas:
        Call Function:
          function: example_function
          model: res.parnter
          res_id: get_ref("base.partner_demo")
          params: ['param1', param2]
          kw: {'extra_param1': get_ref('external_config.extra_param1')}  
```

To call an action server (`ir.actions.server`):
```yml
    002 Call Action Server:
      datas:
        Call Action Server:
          action_server_id: get_ref("custom_module.action_exemple")
          model: res.parnter
          res_id: get_ref("base.partner_demo")
```

## Users

To set groups on a user you can remove previous groups with "unlink all":
```yml
    users:
        datas:
            User Example:
                model: res.users
                force_id: base.user_example
                values:
                    name: Example
                    login: example@test.com
                groups_id:
                    - unlink all
                    - base.group_portal
```
                    
## Other data tools

- delete_all
- delete_domain
- delete_id
- deactivate
- activate
- update_domain
  - search_value_xml_id
      - this option allows to pass an id from xml_id to a domain
      - Can be used with update_domain, activate, deactivate:
  
        ```yml        
                      Deactivate Partner Title doctor:
                          model: res.partner.title
                          search_value_xml_id: base.res_partner_title_doctor
                          deactivate: "[('id', '=', search_value_xml_id)]"
        ```

## Translations

To set the translation of a translatable field, use the **languages** option.
Example:
```yml
    Mail Templates:
        datas:
            Notification:
                model: mail.template
                force_id: mail.notification_template
                languages:
                    - fr_FR
                    - en_US
                values:
                    body_html: |
                        <table>
                            <tbody>
                            Text for french and english
                            </tbody>
                        </table>
```

## Mattermost Notification

To set a Mattermost url and channel where to send notifications:
```yml
    mattermost_channel: my-channel
    mattermost_url: https://mattermost.xxx.com/hooks/dfh654fgh
```

To avoid Mattermost notification, add in main yaml file:
```yml
    no_notification: True
```

## Keepass

Keepass is a tool to store and protect passwords.

Available functions to use stored values in Keepass:
```yml
    password: get_keepass_password('path/passwords.kdbx', 'Folder Name', 'Key Name')
    user: get_keepass_user('path/passwords.kdbx', 'Folder Name', 'Key Name')
    url: get_keepass_url('path/passwords.kdbx', 'Folder Name', 'Key Name')
```

To avoid to repeat path and group in Keepass functions, you can set `keepass_path` and `keepass_group`
```yml
keepass_path: path/passwords.kdbx
keepass_group: Folder Name

my_secret: get_keepass_password('Key Name')
```

3 ways to pass the Keepass password to odoo-configurator :
 - Provide Keepass password with the keepass parameter in command line: `--keepass='mdp***'`
 - Set the `KEEPASS_PASSWORD` environment variable
 - Manually. If it's required odoo-configurator will ask to type the password with the prompt `Keepass Password:`

 In PyCharm, to type the Keepass password, please check the `Emulate terminal in output console` option in your run/debug configuration.

## Bitwarden

Bitwarden is a tool to store and protect passwords. Make sure Bitwarden CLI is installed.

Credentials to connect to Bitwarden Vault can be set by environment variables, please report to the [s6r-bitwarden-cli documentation](https://pypi.org/project/s6r-bitwarden-cli)

An over option is to set the value of `bitwarden_username` and  `bitwarden_password` in yml file. Obviously, do not save password directly in your yml file, use Keepass functions for example.

```yml
bitwarden_username: get_keepass_user('Bitwarden')
bitwarden_password: get_keepass_password('Bitwarden')
```

## Standard CSV Import

Columns in the CSV file must be the technical name of the field.
A column "id" is required to allow update of datas. 

In yml file:

```yml
    import_data:
        import_csv Product Template:
            on_install_only: True
            model: product.template
            name_create_enabled_fields: uom_id,uom_po_id,subscription_template_id
            file_path: ../datas/todoo/product.template.csv
            specific_import: base/import_specific.py
            specific_method: import_partner
            batch_size: 200
            skip_line: 1420
            limit: 100
            context: {'install_mode': True}
```

### Required fields:

  - model
  - file_path

### Optional fields:

  - **name_create_enabled_fields** : List of the fields which are allowed to "Create the record if it doesn't exist"
  - **on_install_only** : Do the csv export only in **Install Mode**
  - **context** : Provide a specific context for imports
  - **specific_import** : Path to a specific Python file
  - **specific_method** : Import method to use form the file **specific_import**
  - **batch_size** : Number of records by load batch
  - **limit** : Maximum number of record to import
  - **skip_line** : index of the record to start with


## Generate YML data file from a model

This configuration will generate a res_partner.yml file in the **config** directory
```yml
Actions:
    import_configurator_model_file:
        Portal Form:
            model: res.partner
            domain: [['is_company', '=', True]]  # Don't use parenthesis in the domain
            order_by: name, ref
            force_export_fields: ["email_formatted", "country_code"]
            excluded_fields: ["email", "country_id"]
```

## Release Configuration

Some configurations need to be executed on every platform until the production release. After that we need to archive these configuration files.
We will store the files in the directory *release_config* for example.
To run all these files, add the **release_directory** parameter in your main configuration file:

```yml
    release_directory: ./release_config
```

To back up the release files after the execution of the production configuration, add the **clear_release_directory** parameter in you production configuration file.

```yml
  clear_release_directory: True
```

## Contributors

* David Halgand
* Michel Perrocheau - [Github](https://github.com/myrrkel)


## Maintainer

This software was created by [Hodei](https://www.hodei.net) formerly Teclib' ERP, 
maintenance is now being handled by [Scalizer](https://www.scalizer.fr).


<div style="text-align: center;">

[![Scaliser](./logo_scalizer.png)](https://www.scalizer.fr)

[![Hooei](./logo_hodei.jpg)](https://www.hodei.net)

</div>