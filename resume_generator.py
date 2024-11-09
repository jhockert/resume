import os
import argparse
import yaml
import jsonschema
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Define the schema for validation
def load_schema(schema_path):
    """Load the JSON schema from a file."""
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)  # Assuming the schema is in YAML format

def validate_yaml(yaml_data, schema):
    """Validate YAML data against the provided schema."""
    jsonschema.validate(instance=yaml_data, schema=schema)

def generate_html(yaml_data, template_path):
    """Generate HTML from YAML data using the provided template."""
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    html_content = template.render(yaml_data)
    return html_content

def generate_pdf(html_content, output_pdf):
    """Generate PDF from HTML content."""
    HTML(string=html_content).write_pdf(output_pdf)

def main():
    parser = argparse.ArgumentParser(description="Generate resume from YAML config file.")
    parser.add_argument("--config", default="config.yaml", type=Path, help="Path to the YAML config file.")
    parser.add_argument("--contact", type=Path, help="Optional contact info file.")
    parser.add_argument("--template", default="template.html.j2", type=Path, help="Path to the HTML template file.")
    parser.add_argument("--schema", default="schema.json", help="Path to the JSON schema file.")
    parser.add_argument("--output-html", default="resume.html", type=Path, help="Path to the output HTML file.")
    parser.add_argument("--output-pdf", default="resume.pdf", type=Path, help="Path to the output PDF file.")
    args = parser.parse_args()

    # Load YAML data
    with open(args.config, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    if args.contact is not None:
        with open(args.contact, 'r', encoding='utf-8') as f:
            contact_data = yaml.safe_load(f)
            config_data = {**config_data, **contact_data}

    # Load JSON schema
    schema = load_schema(args.schema)

    # Validate YAML data against schema
    validate_yaml(config_data, schema)

    # Generate HTML content
    html_content = generate_html(config_data, args.template)

    # Save HTML content to file
    with open(args.output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Generate PDF from HTML content
    generate_pdf(html_content, args.output_pdf)

if __name__ == "__main__":
    main()
