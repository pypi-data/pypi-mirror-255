from django import template

register = template.Library()


def cotton_var(parser, token):
    # Split the token to get variable assignments
    parts = token.split_contents()
    cotton_vars = {}
    for part in parts[1:]:
        key, value = part.split('=')
        cotton_vars[key] = value

    return CottonVarNode(cotton_vars)


register.tag("cotton_var", cotton_var)


class CottonVarNode(template.Node):
    def __init__(self, cotton_vars):
        self.cotton_vars = cotton_vars

    def render(self, context):
        resolved_vars = {}

        # if the same var is already set in context, it's being passed explicitly to override the cotton_var
        # if not, then we resolve it from the context
        for key, value in self.cotton_vars.items():
            # if key in context:
            #     resolved_vars[key] = context[key]
            #     continue
            try:
                resolved_vars[key] = template.Variable(value).resolve(context)
            except (TypeError, template.VariableDoesNotExist):
                resolved_vars[key] = value

        cotton_vars = {'cotton_vars': resolved_vars}

        # Update the global context directly
        context.update(resolved_vars)
        context.update(cotton_vars)
        context['cotton_vars'].update(resolved_vars)

        return ''
