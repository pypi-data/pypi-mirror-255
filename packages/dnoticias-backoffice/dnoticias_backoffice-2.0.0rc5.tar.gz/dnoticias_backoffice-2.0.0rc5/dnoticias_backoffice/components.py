from slippers.templatetags.slippers import register_components


def load_backoffice_slippers():
    register_components({
        "form_input": "components/forms/input.html",
        "form_input_code": "components/forms/input_code.html",
        "form_input_group": "components/forms/input_group.html",
        "form_switch": "components/forms/switch.html",
        "form_switch_label": "components/forms/switch_label.html",
        "form_checkbox": "components/forms/checkbox.html",
        "form_quill": "components/forms/wysiwyg_input.html",
        "form_select2": "components/forms/select2.html",
        "form_select2_empty": "components/forms/select2_empty.html",
        "form_dual_listbox": "components/forms/dual_listbox.html",
        "form_image": "components/forms/image.html",
        "form_checklist": "components/forms/checklist.html",
        "form_input_disabled": "components/forms/input_disabled.html",
        "form_select2_actions": "components/forms/select2_actions.html",
        "form_datetime": "components/forms/datetime.html",
        "form_datetime_range": "components/forms/datetimerange.html",
        "form_date": "components/forms/date.html",
        "form_daterange": "components/forms/daterange.html",
        "form_time": "components/forms/time.html",
        "form_price": "components/forms/price.html",
        "form_group": "components/forms/group.html",
        "form_group_item": "components/forms/group_item.html",
        "form_group_button": "components/forms/group_button.html",
        "form_radiobuttons": "components/forms/radiobuttons.html",

        "kt_section_title": "components/forms/kt_section_title.html",
        "kt_form_footer": "components/forms/kt_form_footer.html",
        "kt_separator": "components/forms/kt_separator.html",

        "modal": "components/modal.html",

        "simple_dategroup": "components/simple_forms/date_group.html",
        "simple_switch_label": "components/simple_forms/switch_label.html",
        "input_hidden": "components/simple_forms/input_hidden.html",
        "button": "components/simple_forms/button.html",

        "menu_item": "components/menu_item.html",
        "menu_category": "components/menu_category.html",

        "datatable_action": "components/datatable/datatable_action.html",
        "datatable_action_item": "components/datatable/datatable_action_item.html",

        "dropdown": "components/dropdown/dropdown.html",
        "dropdown_item": "components/dropdown/item.html",

        "toolbar_button": "components/toolbar/button.html",
        "toolbar_dropdown": "components/toolbar/dropdown.html",
        "toolbar_dropdown_form": "components/toolbar/dropdown_form.html",
        "toolbar_dropdown_item": "components/toolbar/dropdown_item.html",
        "toolbar_dropdown_separator": "components/toolbar/dropdown_separator.html",
        "toolbar_dropdown_user": "components/toolbar/dropdown_user.html",

        "breadcrumb": "components/breadcrumb/breadcrumb.html",
        "breadcrumb_item": "components/breadcrumb/item.html",
        "breadcrumb_bullet": "components/breadcrumb/bullet.html",

        "alert": "components/alert.html",

        "timeline_block": "components/timeline/timeline.html",
        "timeline_item": "components/timeline/item.html",

        "form_dropzone": "components/forms/dropzone.html",
        "form_tooltip": "components/forms/tooltip.html",
    })
