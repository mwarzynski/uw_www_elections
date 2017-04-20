function generateMapData() {
    return [
        ['Provinces', 'tooltip', 'Głosów'],
    {% for v in voivodeships %}
        ['{{ v.name }}', '{{ v.name }}', {{ v.votes }}],
    {% endfor %}
    ];
}

voivodeships = {
    {% for v in voivodeships %}
        '{{ v.name }}': '{{ v.id }}',
    {% endfor %}
}