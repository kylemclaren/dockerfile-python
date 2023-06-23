import os

class TemplateHandler:
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir

    def get_template(self, template_name):
        template_path = os.path.join(self.templates_dir, template_name)
        with open(template_path, 'r') as file:
            template_content = file.read()
        return template_content

    def format_template(self, template_name, **kwargs):
        template = self.get_template(template_name)
        return template.format(**kwargs)
