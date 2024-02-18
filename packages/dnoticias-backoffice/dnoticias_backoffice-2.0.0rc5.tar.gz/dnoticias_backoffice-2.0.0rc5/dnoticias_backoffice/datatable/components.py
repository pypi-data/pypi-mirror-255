from slippers.templatetags.slippers import register_components


def load_slippers():
    register_components({
        "datatable_action": "datatable/components/datatable_action.html",
        "datatable_action_item": "datatable/components/datatable_action_item.html",
    })
