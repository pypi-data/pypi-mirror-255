
{% for evt in events %}
    {
    startDate: new Date( {{ evt.start_date | date:"Y, n - 1, j" }} ),
    endDate: new Date( {{ evt.end_date | date:"Y, n - 1, j" }} ),
    {% if evt.color %}color: "{{ evt.color }}", {% endif %}
    {% if evt.style %}style: "{{ evt.style }}", {% endif %}
    id: "{{ evt.pk }}",
    ct: "{{ evt.ctype_id }}"
    },
{% endfor %}
