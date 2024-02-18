{% load static %}
<script src="{% static 'assets/plugins/custom/datatables/datatables.bundle.js' %}"></script>
<script>
    "use strict";

    {% if extend_js %}
        {% include extended_js_filepath %}
    {% endif %}

    {% if extend_scripts %}
        {% include extended_scripts_filepath %}
    {% endif %}

    {% if filters.fields %}
    document.querySelector('[data-kt-subscription-table-filter="reset"]').addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelectorAll("select[multiple]").forEach((input) => {
            input.value = '';
            input.dispatchEvent(new Event('change'));
        })

        document.querySelectorAll(".daterange").forEach((input) => {
            $(input).val('');
        })
    });
    {% endif %}

    document.querySelectorAll(".daterange").forEach((input) => {
        console.log($(input))
        $(input).daterangepicker({
            autoUpdateInput: false,
            buttonClasses: ' btn',
            applyClass: 'btn-primary',
            cancelClass: 'btn-secondary',
            locale: 'pt',
            autoApply: true,
            {% include "datatable/includes/daterange_locale.js" %}
        }, function(start, end, label) {
            $(input).val(start.format('YYYY-MM-DD') + ' até ' + end.format('YYYY-MM-DD'));
        });
    });

    const MetronicDatatable = function () {
        let table;
        let datatable;
        let filter;

        const refreshFilter = function(filters) {
            if (Object.keys(filters).length > 0) {
                let filterCount = document.querySelector('.filter-count');
                filterCount.innerHTML = Object.keys(filters).length;
                filterCount.style.display = null;
            } else {
                let filterCount = document.querySelector('.filter-count');
                filterCount.innerHTML = '';
                filterCount.style.display = 'none';
            }
        }

        const initDatatable = function() {
            datatable = $("#{{ table_id }}").DataTable({
                searchDelay: 500,
                processing: true,
                serverSide: true,
                order: [],
                stateSave: true,
                stateSaveCallback: function(settings, data) {
                    data.search.filters = {};
                    let count = 0;
                    let filterValue = null;

                    {% for field in filters %}
                        {% if field.name %}
                            filterValue = $('#{{ field.id_for_label }}').val();

                            if (filterValue && filterValue != '' && filterValue != 'null' && filterValue != 'undefined') {
                                data.search.filters['{{ field.name }}'] = filterValue;
                            }
                        {% endif %}
                    {% endfor %}
                    
                    {% if filters.fields %}
                    refreshFilter(data.search.filters);
                    {% endif %}
                    localStorage.setItem('DataTables_{{ table_id }}', JSON.stringify(data));
                },
                stateLoadCallback: function(settings) {
                    const data = JSON.parse(localStorage.getItem('DataTables_{{ table_id }}'));
                    return data;
                },
                stateLoaded: function(settings, data) {
                    if (data.search.search) {
                        document.querySelector('[data-kt-docs-table-filter="search"]').value = data.search.search;
                    }

                    if (data.search.filters) {
                        let filterCount = document.querySelector('.filter-count');
                        let count = 0;
                        let filterValue = null;

                        {% for field in filters %}
                            {% if field.name %}
                                filterValue = data.search.filters['{{ field.name }}'];

                                if (filterValue && filterValue != '' && filterValue != 'null' && filterValue != 'undefined') {
                                    $('#{{ field.id_for_label }}').val(filterValue);
                                    $('#{{ field.id_for_label }}').trigger('change');
                                }
                            {% endif %}
                        {% endfor %}
                        
                        {% if filters.fields %}
                        refreshFilter(data.search.filters);
                        {% endif %}
                    }
                },
                drawCallback: function() {
                    const event = new Event("onDatatableDraw");
                    $('[data-bs-toggle="tooltip"]').tooltip();
                    
                    document.dispatchEvent(event);
                },
                language: {
                    "lengthMenu": "_MENU_",
                    "zeroRecords": "Nenhum registro encontrado",
                    "info": "Mostrando página _PAGE_ de _PAGES_",
                    "infoEmpty": "Nenhum registro disponível",
                    "infoFiltered": "(filtrado de _MAX_ registros no total)",
                    "search": "Procurar",
                    "paginate": {
                        "previous": "Anterior",
                        "next": "Próximo",
                        "first": "Primeiro",
                        "last": "Último"
                    },
                    "processing": "Carregando...",
                },
                ajax: {
                    url: "{{ request.path }}",
                    type: "POST",
                    data: function (data) {
                        data.filters = {};
                        {% for field in filters %}
                            {% if field.name %}
                                data.filters['{{ field.name }}'] = $('#{{ field.id_for_label }}').val();
                            {% endif %}
                        {% endfor %}
                    },
                    headers: {'X-CSRFToken': '{{ csrf_token }}'},
                },
                columns: [
                    {% for column in columns %}
                        {% if column.visible and not column.is_action %}
                        {
                            data: '{{ column.field }}',
                            orderable: {{ column.sortable|yesno:"true,false" }},
                            className: '{{ column.align }}',
                            render: function(data, type, row) {
                                try{
                                    return get_{{column.field}}_html(row);
                                } catch(e) {
                                    return data ? data : `<i class="fas fa-minus"></i>`;
                                }
                            }
                        },
                        {% endif %}
                    {% endfor %}
                    {% if actions %}
                    { data: null },
                    {% endif %}
                ],
                columnDefs: [
                    {% if actions %}
                    {
                        targets: -1,
                        title: 'Acções',
                        orderable: false,
                        className: 'text-end',
                        width: '150px',
                        render: function(data, type, row) {
                            return `
                            {% #datatable_action %}
                                {% for column in columns %}
                                    {% for action in column.actions %}
                                        {% if action.is_separator %}
                                            <div
                                                class="separator separator-dashed {% if action.separator_label %}separator-content my-5{% else %}my-1{% endif %}"
                                                style="display: ${row.{{ action.identifier }}_show ? '' : 'none'};"
                                            >
                                            {{ action.separator_label }}
                                            </div>
                                        {% else %}
                                            {% datatable_action_item identifier=action.identifier name=action.name icon=action.icon method=action.method url=action.url click_function=action.click_function %}
                                        {% endif %}
                                    {% endfor %}
                                {% endfor %}
                            {% /datatable_action %}
                            `;
                        }
                    }
                    {% endif %}
                ],
            })

            table = datatable.$

            datatable.on('draw', function () {
                KTMenu.createInstances();
            });
        }

        const handleSearch = function() {
            const filterSearch = document.querySelector('[data-kt-docs-table-filter="search"]');

            filterSearch.addEventListener('keyup', function (e) {
                datatable.search(e.target.value).draw();
            });
        }

        const handleFilters = function() {
            {% if filters.fields %}
            const filterForm = document.querySelector('[data-kt-subscription-table-filter="filter"]');
            const filterReset = document.querySelector('[data-kt-subscription-table-filter="reset"]');

            filterForm.addEventListener('click', function (e) {
                e.preventDefault();
                datatable.draw();
            });

            filterReset.addEventListener('click', function (e) {
                e.preventDefault();
                datatable.draw();
            });
            {% endif %}
        }

        return {
            init: function () {
                initDatatable();
                handleSearch();
                handleFilters();
            }
        };
    }

    // On document ready
    KTUtil.onDOMContentLoaded(function() {
        MetronicDatatable().init();
        // Toggle tooltips
        $('[data-bs-toggle="tooltip"]').tooltip();
    });
</script>