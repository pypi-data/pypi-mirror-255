from django import template
from django.utils.safestring import mark_safe


def cotton_slot(parser, token):
    try:
        # Splitting by None == splitting by spaces.
        tag_name, slot_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r name missing from x-slot" % token.contents.split()[0]
        )

    nodelist = parser.parse(("end_cotton_slot",))
    parser.delete_first_token()
    return CottonSlotNode(slot_name, nodelist)


class CottonSlotNode(template.Node):
    def __init__(self, slot_name, nodelist):
        self.slot_name = slot_name
        self.nodelist = nodelist

    def render(self, context):
        # Here, we add the rendered content to the context
        # Todo, we need to ensure these vars are scoped to the parent component only
        if "cotton_slots" not in context:
            context.update({"cotton_slots": {}})

        output = self.nodelist.render(context)

        # delete cotton_slots key for slot_name
        if self.slot_name in context["cotton_slots"]:
            del context["cotton_slots"][self.slot_name]

        context["cotton_slots"][self.slot_name] = mark_safe(output)
        return ""
