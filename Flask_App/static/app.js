let map;
var currWindow = false;

function initMap() {
    fetch("/stations").then(response => {
        return response.json();
    }).then(data => {

        map = new google.maps.Map(document.getElementById("map"), {
            center: { lat: 53.349834, lng: -6.260310 },
            zoom: 14,
        });

        data.forEach(station => {

            const marker = new google.maps.Marker({
                position: { lat: station.position_lat, lng: station.position_lng },
                map: map,
            });
            marker.addListener("click", () => {
                if (currWindow) {
                    currWindow.close();
                }
                const infowindow = new google.maps.InfoWindow({
                content: "<h3>" + station.name + "</h3>"
                + "<p><b>Available Bikes: </b>" + station.available_bikes + "</p>"
                + "<p><b>Available Stands: </b>" + station.available_bike_stands + "</p>"
                + "<p><b>Parking Slots: </b>" + station.available_bike_stands + "</p>"
                + "<p><b>Status: </b>" + station.status + "</p>"
                });
                currWindow = infowindow;
                infowindow.open(map, marker);
                weeklyChart(station.number);
                hourlyChart(station.number);
            });
        });
    }).catch(err => {
        console.log("Error:", err);
    })
}


// Function to populate the select dropdown menu for possible dates
function stationDropDown() {
    fetch("/static_stations").then(response => {
        return response.json();
    }).then(data => {

    var station_output = "<label for='station_option'>Choose a station: </label>"
    + "<select name='station_option' id='station_option' onchange='setValue(this)'>"
    + "<option value='' disabled selected> ------------- </option><br>";

    data.forEach(station => {
        station_output += "<option value=" + station.number + ">" + station.name + "</option><br>";
    })

    station_output += "</select>";
    document.getElementById("station_selection").innerHTML = station_output;
    }).catch(err => {
        console.log("Error:", err);
    })
}

// Function to set user choice station and trigger other functions
function setValue(control) {
    var choice = control.value;
    showSelected(choice);
    weeklyChart(choice);
    hourlyChart(choice);
}

// Function to display info window for chosen station
function showSelected(chosenStation) {
    fetch("/stations").then(response => {
        return response.json();
    }).then(data => {

        data.forEach(station => {
            if (station.number == chosenStation) {

                if (currWindow) {
                    currWindow.close();
                }

                const marker = new google.maps.Marker({
                    position: { lat: station.position_lat, lng: station.position_lng },
                    map: map,
                });

                const infowindow = new google.maps.InfoWindow({
                    content: "<h3>" + station.name + "</h3>"
                    + "<p><b>Available Bikes: </b>" + station.available_bikes + "</p>"
                    + "<p><b>Available Stands: </b>" + station.available_bike_stands + "</p>"
                    + "<p><b>Parking Slots: </b>" + station.available_bike_stands + "</p>"
                    + "<p><b>Status: </b>" + station.status + "</p>"
                });
                currWindow = infowindow;
                infowindow.open(map, marker);
                weeklyChart(station.number);
                hourlyChart(station.number);
            }
        });
    }).catch(err => {
        console.log("Error:", err);
    })
}


// Function to display weekly analysis chart
function weeklyChart(station_number) {
    fetch("/occupancy/"+station_number).then(response => {
            return response.json();
        }).then(data => {

        var chosenStationName;
        var analysis_title_output = "";

        Stn_Name = "";
        bike_stands = 0;
        bikes_free = 0;
        Iter_Count = 0;
        Day_Name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        Day_Name_Abrv = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"];
        Average = [];
        for (i = 0; i < Day_Name.length; i++) {
            data.forEach(obj => {
                chosenStationName = obj.name;

                if (obj.DayName == Day_Name[i]) {
                    Stn_Name = obj.address;
                    bike_stands = obj.Avg_bike_stands;
                    bikes_free = bikes_free + obj.Avg_bikes_free;
                    Iter_Count = Iter_Count + 1;
                }
            })
            Average.push(bikes_free/Iter_Count);
            bikes_free = 0;
            Iter_Count = 0;
        }

         chart_data = new google.visualization.DataTable();
         options = {
             title: 'Average Availability Per Day',
             width: '700', height: '450',
             vAxis: {
                title: 'Number of Bikes'
             }
        };
        chart_data.addColumn('string', "Week_Day_No");
        chart_data.addColumn('number', "Average Bikes Available");

        for (i = 0; i < Day_Name.length; i++) {
            chart_data.addRow([Day_Name_Abrv[i], Average[i]]);
        }

        analysis_title_output = "<h2>" + chosenStationName + "</h2>";
        document.getElementById("analysis_title").innerHTML = analysis_title_output;

        chart = new google.visualization.ColumnChart(document.getElementById("weekly_chart"));
        chart.draw(chart_data, options);
    });
}


// Function to display hourly analysis chart
function hourlyChart(station_number) {
    fetch("/hourly/"+station_number).then(response => {
            return response.json();
        }).then(data => {

        chart_data = new google.visualization.DataTable();
        options = {
            title: 'Average Availability Per Hour',
             width: '700', height: '450',
             hAxis: {
                title: 'Hour of the Day (00:00)',
             },
             vAxis: {
                title: 'Number of Bikes'
             }
        };
        chart_data.addColumn('timeofday', "Time of Day");
        chart_data.addColumn('number', "Average Bikes Available");

        for (i = 0; i < data.length; i++) {
            chart_data.addRow([[data[i]['Hourly'], 0, 0], data[i]['Avg_bikes_free']]);
        }
        chart = new google.visualization.LineChart(document.getElementById('hour_chart'));
        chart.draw(chart_data, options);
    });
}


