from django import template
from django.template import Node, Context
from django.template.base import TextNode, NodeList
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


def cotton_component(parser, token):
    bits = token.split_contents()
    tag_name = bits[0]
    template_path = bits[1]

    kwargs = {}
    for bit in bits[2:]:
        key, value = bit.split("=")
        kwargs[key] = value

    nodelist = parser.parse(("end_cotton_component",))
    parser.delete_first_token()

    return CottonComponentNode(nodelist, template_path, kwargs)


class CottonComponentNode(Node):
    def __init__(self, nodelist, template_path, kwargs):
        self.nodelist = nodelist
        self.template_path = template_path
        self.kwargs = kwargs
        self.named_slots = {}

    def render(self, context):
        local_context = context.flatten()

        resolved_kwargs = {}
        for key, value in self.kwargs.items():
            try:
                resolved_value = template.Variable(value).resolve(context)
                resolved_kwargs.update({key: resolved_value})
            except TypeError:
                resolved_kwargs.update({key: value})
            except template.VariableDoesNotExist:
                resolved_kwargs.update({key: value})

        # Add the remainder as the default slot
        rendered = self.nodelist.render(context)
        local_context.update({"slot": rendered})

        slots = context.get("cotton_slots", {})
        local_context.update(slots)

        local_context.update(resolved_kwargs)

        # save attrs dict to context for
        local_context.update({"attrs_dict": resolved_kwargs})

        # Provide all of the attrs as a string to pass to the component
        # todo: should we be having defined variables in the component and this string only includes the remainder?
        # because of the issue where django changes <div {{attrs}}> to <div {{attrs}}="">, it leaves all attrs after the
        # initial, without quotes around the value
        def ensure_quoted(value):
            if value.startswith('"') and value.endswith('"'):
                return value
            else:
                return f'"{value}"'

        attrs = " ".join(
            [f"{key}={ensure_quoted(value)}" for key, value in self.kwargs.items()]
        )
        local_context.update({"attrs": mark_safe(attrs)})

        rendered = render_to_string(self.template_path, local_context)

        # check for with vars to add
        cotton_vars = local_context.get("cotton_vars", {})
        if len(cotton_vars):
            with_statements = " ".join(
                [
                    f"{key}={value}"
                    for key, value in context.items()
                    if key in self.cotton_vars
                ]
            )
            rendered = "{% with " + with_statements + " %}" + rendered + "{% endwith %}"
            del local_context["cotton_vars"]

        return rendered
