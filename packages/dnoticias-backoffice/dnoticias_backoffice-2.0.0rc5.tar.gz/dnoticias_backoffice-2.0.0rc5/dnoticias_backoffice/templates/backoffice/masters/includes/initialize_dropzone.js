Dropzone.autoDiscover = false;
var attachmentsDropzone;

{% var url=upload_url|default:'upload-attachment' %}

$(document).ready(function () {
    var id = '#{{ input.auto_id }}_dropzone';

    attachmentsDropzone = new Dropzone(id, {
        url: "{% url url %}",
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        },
        addRemoveLinks: true,
        parallelUploads: 20,
        maxFilesize: 20, // Max filesize in MB
        success: function (file, response) {
            console.log(response);
            var attachmentsValue = $("#{{ input.auto_id }}").val();
            var attachmentsIds = attachmentsValue.split(",").filter(Boolean);
            attachmentsIds.push(response.pk);
            $("#{{ input.auto_id }}").val(attachmentsIds.join(","));
        }
    }); 
});