import os
import subprocess
import argparse
from pathlib import Path

import yaml
import jsonschema
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Define the schema for validation
def load_schema(schema_path):
    """
    Load and parse a JSON schema file.

    Args:
        schema_path (str or Path): The file path to the JSON schema.

    Returns:
        dict: The parsed schema as a dictionary.
    """
    with open(schema_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)  # Assuming the schema is in YAML format

def validate_yaml(yaml_data, schema):
    """
    Validate YAML data against a JSON schema.

    Args:
        yaml_data (dict): The data to validate.
        schema (dict): The schema to validate against.

    Raises:
        jsonschema.exceptions.ValidationError: If validation fails.
    """
    jsonschema.validate(instance=yaml_data, schema=schema)

def get_git_tag():
    """
    Retrieve the current Git tag, if available.

    Returns:
        str: The current Git tag, or "N/A" if not available.
    """
    try:
        git_tag = subprocess.check_output(["git", "describe", "--tags"], text=True).strip()
    except subprocess.CalledProcessError:
        git_tag = "N/A"
    return git_tag

def generate_html(output, yaml_data, template_path):
    """
    Generate HTML content from YAML data using a Jinja2 template.

    Args:
        output (str or Path): The output path for the generated HTML file.
        yaml_data (dict): The data to render in the template.
        template_path (str or Path): Path to the HTML template file.

    Returns:
        str: The rendered HTML content.
    """
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    html_content = template.render(yaml_data)

    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return html_content

def generate_pdf(html_content, output_pdf):
    """
    Generate a PDF file from HTML content.

    Args:
        html_content (str): The HTML content to convert to PDF.
        output_pdf (str or Path): The output path for the generated PDF.
    """
    HTML(string=html_content).write_pdf(output_pdf)

def parse_args():
    """
    Parse command-line arguments for the script.

    Returns:
        argparse.Namespace: The parsed arguments as a namespace object.
    """
    parser = argparse.ArgumentParser(description="Generate resume from YAML config file.")
    parser.add_argument("--config", default="config.yaml", type=Path, help="Path to the YAML config file.")
    parser.add_argument("--template", default="template.html.j2", type=Path, help="Path to the HTML template file.")
    parser.add_argument("--schema", default="schema.json", help="Path to the JSON schema file.")
    parser.add_argument("--static", default="static", type=Path, help="Path to the static folder.")
    parser.add_argument("--output-html", default="resume.html", type=Path, help="Path to the output HTML file.")
    parser.add_argument("--output-pdf", default="resume.pdf", type=Path, help="Path to the output PDF file.")
    parser.add_argument("--contact", type=Path, help="Optional contact info file.")
    return parser.parse_args()

def main():
    """
    Main function to generate PDF and HTML resume files from YAML configuration.

    This function:
    - Parses command-line arguments.
    - Loads configuration and optional contact information from YAML files.
    - Validates the configuration against a schema.
    - Renders HTML using the provided template and configuration data.
    - Converts the rendered HTML to a PDF file.
    """
    args = parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    # Load optional private contact info
    if args.contact is not None:
        with open(args.contact, 'r', encoding='utf-8') as f:
            private_contact_data = yaml.safe_load(f)['contact']
            config_data['contact'] = config_data['contact'] | private_contact_data

    schema = load_schema(args.schema)
    validate_yaml(config_data, schema)

    # Set config data
    config_data['git_tag'] = get_git_tag()
    config_data['static'] = args.static.absolute()

    html_content = generate_html(args.output_html, config_data, args.template)
    generate_pdf(html_content, args.output_pdf)

if __name__ == "__main__":
    main()
