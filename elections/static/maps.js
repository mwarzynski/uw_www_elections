names = {'PL-ZP': 'zachodniopomorskie',
         'PL-PM': 'pomorskie',
         'PL-WN': 'warmińsko-mazurskie',
         'PL-PD': 'podlaskie',
         'PL-LB': 'lubuskie',
         'PL-WP': 'wielkopolskie',
         'PL-MZ': 'mazowieckie',
         'PL-LU': 'lubelskie',
         'PL-DS': 'dolnośląskie',
         'PL-KP': 'kujawsko-pomorskie',
         'PL-LD': 'łódzkie',
         'PL-OP': 'opolskie',
         'PL-SL': 'śląskie',
         'PL-SK': 'świętokrzyskie',
         'PL-MA': 'małopolskie',
         'PL-PK': 'podkarpackie'};

google.charts.load('current', {
    'packages': ['geochart']
});

google.charts.setOnLoadCallback(drawRegionsMap);

function drawRegionsMap() {

    var data = google.visualization.arrayToDataTable(generateMapData());

    var options = {
        resolution: 'provinces',
        region: 'PL',
        datalessRegionColor: '#123456',
        colorAxis: {colors: ['#fff0ef', '#ea3023']}
    };

    var chart = new google.visualization.GeoChart(document.getElementById('map'));

    chart.draw(data, options);

    google.visualization.events.addListener(chart, 'regionClick', regionClickHandler);

    function regionClickHandler(data) {
        window.location = "/voivodeship/" + voivodeships[names[data['region']]];
    }
}

window.onload = function() {
    drawRegionsMap();
};

window.onresize = function () {
    drawRegionsMap();
};
