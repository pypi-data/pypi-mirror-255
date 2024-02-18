#!/usr/bin/env python

import os
import logging

########################################################################################################################


def get_prefix(string):
    """
    name: "\U0001f680 Team"
    title: "\U0001f680 <team_name>"

    name: "\U0001f3c6 Goal"
    title: "\U0001f3c6 g-<team_alias>: <IaC|CI/CD|Backup|Monitoring|Disaster Recovery>"

    name: "\U0001f451 Epic"
    title: "\U0001f451 e-<team_alias>:"

    name: "\U0001f451 Maintenance Epic"
    title: "\U0001f451 me-<team_alias>: <goal_type> Maintenance 2024 Q1"

    name: "\U0001f4c7 Collection"
    title: "\U0001f4c7 c-<team_alias>:"

    name: "\U0001f4c7 Collection Maintenance"
    title: "\U0001f4c7 mc-<team_alias>:"
    """

    line_prefix = 'title: "'
    if string.startswith(line_prefix):
        string = string.split(line_prefix)[-1]
    title_parts = string.split()

    # When the issue title is only one character (should not happen)
    if len(title_parts) == 1:
        return title_parts[0][0]

    if len(title_parts) > 1:
        # Most cases, e.g. issues with the following titles:
        # 🏆 g-act: Disaster Recovery
        # 👑 e-act: Monitoring improvements and ideas
        # 👑 me-act: Monitoring Maintenance 2024 Q1
        # 📇 c-act: azure-key-vault-report updates
        # 📇 mc-act: azure-key-vault-alert test
        if "-" in title_parts[1] and ":" in title_parts[1]:
            a = title_parts[0]
            b = title_parts[1].split("-")[0]
            return f"{a} {b}"

        # For Goal issue titles, e.g. issues with the following title
        # 🚀 Project Portal
        return title_parts[0]

    # When no issue title
    return ""


class IssueTemplates(object):
    """
    Reads the specified GitHub template files in the specified directory.
    Returns the template which correspondences with the issue title prefix provided.
    Optionally replaces placeholders elements in templates and writes the templates.

    Attributes
    ----------

    templates_dir : str
        Full path to the directory of the issue templates.
    template_filenames : list
        The list of template filenames which should be processed.
    team_name : str
        The string that will replace all occurrences of 'team_name_placeholder'
    team_name_placeholder : str
        The value of this will all be replaced by the value of the 'team_name'
    team_alias : str
        The string that will replace all occurrences of 'team_alias_placeholder'
    team_alias_placeholder : str
        The value of this will all be replaced by the value of the 'team_alias'
    templates_version : str
        The version to add to the template(s) header


    Methods
    -------
    handle_templates(write_templates=False)
        Parses through every 'template_filenames' and try to find the file in the 'templates_dir'.
        If the file is found the read_template() method is called.
        If the 'write_templates' argument is set to 'True' the write_template() method is called.
    read_template(template_file)
        Read the issue template file. Calls the replace_placeholder() method on each line to replace the placeholders
        and stores the result as a dict and adds it to the template list.
    write_template(template)
        Read the provided template dict and write it to file.
    replace_placeholder(string):
        Replace the placeholders in the provided string (line)
    get_template(title, write_templates=False)
        Parses through the list of templates. If the provided title starts with the prefix of the current template
        in list it will be return. If not it will continue to next template in the list.
    """

    def __init__(self, templates_dir, template_filenames,
                 team_name, team_name_placeholder, team_alias, team_alias_placeholder,
                 templates_version):
        """
        Parameters
        ----------
        templates_dir : str
            Full path to the directory of the issue templates.
        template_filenames : list
            The list of template filenames which should be processed.
        team_name : str
            The string that will replace all occurrences of 'team_name_placeholder'
        team_name_placeholder : str
            The value of this will all be replaced by the value of the 'team_name'
        team_alias : str
            The string that will replace all occurrences of 'team_alias_placeholder'
        team_alias_placeholder : str
            The value of this will all be replaced by the value of the 'team_alias'
    templates_version : str
        The version to add to the template(s) header
        """

        self.templates_dir = templates_dir

        self.template_filenames = template_filenames
        if isinstance(template_filenames, str):
            self.template_filenames = template_filenames.split()

        self.team_name = team_name
        self.team_name_placeholder = team_name_placeholder
        self.team_alias = team_alias
        self.team_alias_placeholder = team_alias_placeholder
        if not templates_version:
            self.templates_version = ""
        else:
            self.templates_version = templates_version

        self.templates = []

    def handle_templates(self, write_templates=False):
        """Parses through every 'template_filenames' and try to find the file in the 'templates_dir'."""

        if not os.path.isdir(self.templates_dir):
            logging.info(f"'{self.templates_dir}' dir does not exists.")
            return False

        logging.info(f"looking in dir '{self.templates_dir}'..")
        # Parse through every filename in the list of filenames
        for item in self.template_filenames:
            template_file = os.path.join(self.templates_dir, item)
            if os.path.isfile(template_file):
                # If the specific filename exists as a file in the templates dir it will be read and added
                # to the list of templates as a dict
                template = self.read_template(template_file)
                if template:
                    self.templates.append(template)
                    # If write_templates is set to True the template dict will be written to
                    # file in templates_dir directory (with the current filename)
                    if write_templates:
                        self.write_template(item, template)

        if self.templates:
            return True

    def read_template(self, template_file):
        """Read the issue template file. Calls the 'replace_placeholder' method on each line to replace the placeholders
        and stores the result as a dict and adds it to the templates list.

        Parameters
        ----------
        template_file : str
            The template file to read.
        """

        with open(template_file) as f:
            template = {}
            # Reads each line of the template files. The lines at the top, between the --- lines, are treated as
            # headers. The line that starts with 'title: ' will contain the character used as the prefix.
            # The prefix is a unicode value which is converted to ASCII when returned.
            # The templates version are not read from file, as the version passed as an parameter will be
            # used when writing the templates.
            for line in f.readlines():
                if not template and line.startswith("---"):
                    template["header"] = ""
                elif line.startswith("version:"):
                    continue
                elif template and not line.startswith("---") and "body" not in template:
                    template["header"] += self.replace_placeholder(line)
                    if line.startswith("title: "):
                        prefix = get_prefix(line)
                        template["prefix"] = prefix
                elif template and line.startswith("---"):
                    template["body"] = ""
                elif not line.startswith("---") and "body" in template:
                    template["body"] += self.replace_placeholder(line)
            template["name"] = template_file.split("/")[-1]
            template["version"] = self.templates_version
            return template

    def write_template(self, filename, template):
        """Read the provided template dict and write it to file.

        Parameters
        ----------
        filename : str
            The name of the file to be written to.
        template : dict
            The template dictionary object.
        """

        if not os.path.isdir(self.templates_dir):
            os.makedirs(self.templates_dir)

        header = template.get("header")
        body = template.get("body")
        content = "---\n"
        for line in header.splitlines():
            content += f"{line}\n"
        content += f'version: "{template.get("version")}"\n'
        content += "---\n"
        for line in body.splitlines():
            content += f"{line}\n"

        with open(os.path.join(self.templates_dir, filename), "w") as f:
            f.write(content)

    def replace_placeholder(self, string):
        """Replace the placeholders in the provided string.

        Parameters
        ----------
        string : str
            The string which contains the placeholders to be replaced.
        """

        row = string.replace(self.team_name_placeholder, self.team_name)
        row = row.replace(self.team_alias_placeholder, self.team_alias)
        return row

    def get_template(self, title, write_templates=False):
        """Parses through the list of templates. If the provided title starts with the prefix of the current template
        in list it will be returned. If not it will continue to next template in the templates list.

        Parameters
        ----------
        title : str
            The title of the GitHub issue.
        write_templates : boolean
            Will be passed to the 'handle_templates' method. If set to 'True' the 'write_template' method will be called
            at the end of the 'handle_templates' method.
        """

        if not self.handle_templates(write_templates=write_templates):
            return

        if not title:
            logging.error("No issue template title")
            return

        if not self.templates_dir:
            logging.error("No templates dir.")
            return

        logging.info(f"Looking for template matching title: '{title}'..")
        for template in self.templates:
            prefix = template.get("prefix")
            name = template.get("name")
            if not prefix:
                logging.info(f"Prefix: '{prefix}'. Using '{name}' template.")
                return template.get("body")

            if title.encode('unicode-escape').decode('ASCII').startswith(prefix):
                logging.info(f"Prefix: '{prefix}'. Using '{name}' template.")
                return template.get("body")

            if title.startswith(prefix):
                logging.info(f"Prefix: '{prefix}'. Using '{name}' template.")
                return template.get("body")
