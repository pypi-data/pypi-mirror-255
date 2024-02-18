#!/usr/bin/env python

import logging
import argparse

try:
    from .gh_issue_templates import IssueTemplates
except:
    from gh_issue_templates import IssueTemplates


########################################################################################################################


def main():
    """Creates a issue_template object and passes the argparse arguments.
    Prints the output from the issue_template.get_template method"""
    
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s', level=logging.INFO)

    # The list of key vaults to check passed as command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-T", "--title", type=str,
                        help="The title of issue created.")

    parser.add_argument("-t", "--template_filenames", nargs='+',
                        default="c_epic.md d_collection.md e_task.md",
                        help="List of template filenames.\n"
                             "Valid filenames: a_team.md b_goal.md c_epic.md d_collection.md e_task.md"
                             "Default: c_epic.md d_collection.md e_task.md"
                        )

    parser.add_argument("-d", "--templates_dir", type=str, default='',
                        help="Full path to the directory of the issue templates.'")

    parser.add_argument("-n", "--team_name", type=str,
                        default='Azure Champions Team',
                        help="Value which replaces the '--team_name_placeholder' values.\n"
                             "This is is used in team and goal templates.\n"
                             "Default: Azure Champions Team")

    parser.add_argument("-N", "--team_name_placeholder", type=str,
                        default='<team_name>',
                        help="Occurrences of this value will be replaced with the value of '--team_name'.\n"
                             "Default: <team_name>")

    parser.add_argument("-a", "--team_alias", type=str,
                        help="Value which replaces the '--team_alias_placeholder' values")

    parser.add_argument("-A", "--team_alias_placeholder", type=str,
                        default='<team_alias>',
                        help="Occurrences of this value will be replaced with the value of '--team_alias'")

    parser.add_argument("-w", "--write_templates", type=str,
                        help="Update with template from repo")

    parser.add_argument("-V", "--templates_version", type=str,
                        help="The version that will be written to the template(s) header")

    args = parser.parse_args()

    title = args.title
    templates_dir = args.templates_dir
    template_filenames = args.template_filenames
    team_name = args.team_name
    team_name_placeholder = args.team_name_placeholder
    team_alias = args.team_alias
    team_alias_placeholder = args.team_alias_placeholder
    if "true" in str(args.write_templates).lower():
        write_templates = True
    else:
        write_templates = False
    templates_version = args.templates_version

    for k, v in sorted(vars(args).items()):
        logging.info(f"Argument '{k}': '{v}'")

    if len(template_filenames) == 1:
        template_filenames = template_filenames[0].split()

    if not isinstance(team_alias, str) or not len(team_alias) == 3:
        logging.error("team_alias length must be exactly 3 characters.")
        exit(2)

    issue_template = IssueTemplates(templates_dir, template_filenames,
                                    team_name, team_name_placeholder, team_alias, team_alias_placeholder,
                                    templates_version)

    if write_templates:
        logging.info(f"Adding templates..")
        issue_template.handle_templates(write_templates=write_templates)
        if title:
            template = issue_template.get_template(title)
            if template:
                logging.info(f"OK. Outputting template for '{title}' type issue..")
                return template
        return

    template = issue_template.get_template(title, write_templates=write_templates)
    if template:
        logging.info(f"OK. Outputting template to be used with issue '{title}'..")
        return template

    logging.error(f"Template for '{title}' type issue not found in '{templates_dir}'")

########################################################################################################################


if __name__ == '__main__':
    output = main()
    if output:
        print(output)
