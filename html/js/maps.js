names = {'PL-ZP': 'zachodniopomorskie',
         'PL-PM': 'pomorskie',
         'PL-WN': 'warmińskomazurskie',
         'PL-PD': 'podlaskie',
         'PL-LB': 'lubuskie',
         'PL-WP': 'wielkopolskie',
         'PL-MZ': 'mazowieckie',
         'PL-LU': 'lubelskie',
         'PL-DS': 'dolnośląskie',
         'PL-KP': 'kujawskopomorskie',
         'PL-LD': 'łódzkie',
         'PL-OP': 'opolskie',
         'PL-SL': 'śląskie',
         'PL-SK': 'świętokrzyskie',
         'PL-MA': 'małopolskie',
         'PL-PK': 'podkarpackie'};

google.charts.load('current', {
    'packages': ['geochart']
});kujawsko-pomorskie

google.charts.setOnLoadCallback(drawRegionsMap);

function drawRegionsMap() {

    var data = google.visualization.arrayToDataTable([
        ['Provinces', 'tooltip', 'Głosów'],
        ['PL-ZP', 'zachodniopomorskie', 400],
        ['PL-PM', 'pomorskie', 500],
        ['PL-WN', 'warmińskomazurskie', 400],
        ['PL-PD', 'podlaskie', 600],
        ['PL-LB', 'lubuskie', 400],
        ['PL-WP', 'wielkopolskie', 800],
        ['PL-MZ', 'mazowieckie', 900],
        ['PL-LU', 'lubelskie', 300],
        ['PL-DS', 'dolnośląskie', 700],
        ['PL-KP', 'kujawskopomorskie', 400],
        ['PL-LD', 'łódzkie', 400],
        ['PL-OP', 'opolskie', 400],
        ['PL-SL', 'śląskie', 500],
        ['PL-SK', 'świętokrzyskie', 600],
        ['PL-MA', 'małopolskie', 400],
        ['PL-PK', 'podkarpackie', 700]
    ]);

    var options = {
        resolution: 'provinces',
        region: 'PL',
        datalessRegionColor: 'white',
        datalessRegionColor: '#123456',
        colorAxis: {colors: ['#fff0ef', '#ea3023']}
    };

    var chart = new google.visualization.GeoChart(document.getElementById('map'));

    chart.draw(data, options);

    google.visualization.events.addListener(chart, 'regionClick', regionClickHandler);

    function regionClickHandler(data) {
        window.location = names[data['region']] + ".html"
    }
}

window.onload = function() {
    drawRegionsMap();
};

window.onresize = function () {
    drawRegionsMap();
};
