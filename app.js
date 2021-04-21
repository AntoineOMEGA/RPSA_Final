var new_marker_description = "null";
var new_marker_title = "null";
var new_marker_lat = null;
var new_marker_lng = null;
var new_marker_category = "null";
var locations = [];


var layer = new L.StamenTileLayer("terrain");
var mymap = new L.Map("mapid", {});

mymap.addLayer(layer);
var markerGroup = L.layerGroup().addTo(mymap);

var pages = [
	{ "name": "login-page", "active": true, "live": true },
	{ "name": "register-page", "active": false, "live": true },
	{ "name": "home-page", "active": false, "live": true },
];

var setActivePage = function (active_page) {
	pages.forEach(function (page) {
		if (active_page == page.name & page.live) {
			page.active = true;
		} else {
			page.active = false;
		}
		displayActivePage();
	})
};

var displayActivePage = function () {
	pages.forEach(function (page) {
		var page_element = document.querySelector("#" + page.name);
		if (page.active) {
			page_element.style.display = "block";
			if (page.name == "home-page") {
				mymap.invalidateSize();
				mymap.locate({ setView: true, maxZoom: 12 });
			}
		} else {
			if (page.live) {
				page_element.style.display = "none";
			}
		}
	})
};

var register = function () {
	firstname_field = document.querySelector("#registration-firstname-input");
	lastname_field = document.querySelector("#registration-lastname-input");
	email_field = document.querySelector("#registration-email-input");
	password_field = document.querySelector("#registration-password-input");
	new_user_firstname = firstname_field.value;
	new_user_lastname = lastname_field.value;
	new_user_email = email_field.value;
	new_user_password = password_field.value;

	fetch("http://localhost:8080/users", {
		method: "POST",
		body: "firstname=" + encodeURIComponent(new_user_firstname.toString()) + "&lastname=" + encodeURIComponent(new_user_lastname.toString()) + "&email=" + encodeURIComponent(new_user_email.toString()) + "&password=" + encodeURIComponent(new_user_password.toString()),
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		credentials: "include"
	}).then(function (response) {
		console.log(response.status);

		//ONLY DO THIS IF RESPONSE STATUS IS RIGHT
		if (response.status == 201) {
			firstname_field.value = "";
			lastname_field.value = "";
			email_field.value = "";
			password_field.value = "";
			setActivePage("login-page");
		} else {
			response.text().then(function (data) {
				window.alert(data);
			});
		}

	});
};

var login = function () {
	email_field = document.querySelector("#login-email-input");
	password_field = document.querySelector("#login-password-input");

	user_email = email_field.value;
	user_password = password_field.value;

	fetch("http://localhost:8080/sessions", {
		method: "POST",
		body: "email=" + encodeURIComponent(user_email.toString()) + "&password=" + encodeURIComponent(user_password.toString()),
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		credentials: "include"
	}).then(function (response) {
		console.log(response.status);
		response.text().then(function (data) {
			if (response.status == 201) {
				email_field.value = "";
				password_field.value = "";
				setActivePage("home-page");
				getLocations();
			} else {
				alert(data);
			}
		});
	});
};

var checkAuthentication = function () {
	fetch("http://localhost:8080/sessions", {
		method: "GET",
		credentials: "include"
	}).then(function (response) {
		console.log(response.status);
		response.text().then(function (data) {
			if (response.status == 200) {
				setActivePage("home-page");
				getLocations();
			} else {
				setActivePage("login-page");
				console.log(data);
			}
		});

	});
};

var logout = function () {
	fetch("http://localhost:8080/sessions", {
		method: "DELETE",
		credentials: "include"
	}).then(function (response) {
		console.log(response.status);
		setActivePage("login-page");
	});
};

var getLocations = function () {
	fetch("http://localhost:8080/locations", {
		method: "GET",
		credentials: "include"
	}).then(function (response) {
		console.log(response.status);
		response.json().then(function (data) {
			locations = data.locations;
			generateMarkers();
		});
	});
};

var generateMarkers = function () {
	//REMOVE ALL MARKERS BEFORE REMAKING THEM
	mymap.removeLayer(markerGroup);
	markerGroup = L.layerGroup().addTo(mymap);
	for (i = 0; i < locations.length; i++) {
		var marker = L.marker([parseFloat(locations[i].latitude), parseFloat(locations[i].longitude)]).addTo(markerGroup);
		marker.bindPopup("<b>" + locations[i].title + "</b><br>" + locations[i].description + "<br> <i>Category - " + locations[i].category + ".</i> <br> <button class='delete' id='" + locations[i].id + "' onclick='deleteLocation(" + locations[i].id + ")'>Delete</button> <button class='update' id='" + locations[i].id + "' onclick='updateActive(" + locations[i].id + ")'>Update</button> <i>ID: " + locations[i].id + "</i>").openPopup();
	}
};

var popup = L.popup();

function onMapClick(e) {
	new_marker_lat = e.latlng.lat;
	new_marker_lng = e.latlng.lng;

	popup
		.setLatLng([new_marker_lat, new_marker_lng])
		.setContent("You clicked the map at " + new_marker_lat + " " + new_marker_lng)
		.openOn(mymap);
}

var submit = document.querySelector("#submit-button");
submit.onclick = function () {
	title_field = document.querySelector("#new-title");
	description_field = document.querySelector("#new-description");
	category_field = document.querySelector("#new-category");
	new_marker_title = title_field.value;
	new_marker_description = description_field.value;
	new_marker_category = category_field.value;
	fetch("http://localhost:8080/locations", {
		method: "POST",
		body: "title=" + encodeURIComponent(new_marker_title.toString()) + "&latitude=" + encodeURIComponent(new_marker_lat.toString()) + "&longitude=" + encodeURIComponent(new_marker_lng.toString()) + "&description=" + encodeURIComponent(new_marker_description.toString()) + "&category=" + encodeURIComponent(new_marker_category.toString()),
		headers: {
			"Content-Type": "application/x-www-form-urlencoded"
		},
		credentials: "include"
	}).then(function (response) {
		console.log(response.status);
		getLocations();
		title_field.value = "";
		description_field.value = "";
		category_field.value = "";
	});
}

var deleteLocation = function (id) {
	var remove = confirm("Are you sure you want to remove this location?");
	if (remove) {
		fetch("http://localhost:8080/locations/" + id, {
			method: "DELETE",
			credentials: "include"
		}).then(function (response) {
			console.log(response.status);
			getLocations();
		});
	}
}

var updateActive = function (id) {
	locations.forEach(function (location) {
		if (id == location.id) {
			var submission = document.querySelector("#submission");
			submission.style.display = "none";
			var update = document.querySelector("#update");
			update.style.display = "block";

			var title_field = document.querySelector("#update-title");
			var description_field = document.querySelector("#update-description");
			var category_field = document.querySelector("#update-category");

			title_field.value = location.title;
			description_field.value = location.description;
			category_field.value = location.category;

			var update_button = document.querySelector("#update-button");
			update_button.onclick = function () {
				var updated_marker_title = title_field.value;
				var updated_marker_description = description_field.value;
				var updated_marker_category = category_field.value;

				fetch("http://localhost:8080/locations/" + id, {
					method: "PUT",
					body: "title=" + encodeURIComponent(updated_marker_title.toString()) + "&description=" + encodeURIComponent(updated_marker_description.toString()) + "&category=" + encodeURIComponent(updated_marker_category.toString()),
					headers: {
						"Content-Type": "application/x-www-form-urlencoded"
					},
					credentials: "include"
				}).then(function (response) {
					console.log(response.status);
					getLocations();
					title_field.value = "";
					description_field.value = "";
					category_field.value = "";
					update.style.display = "none";
					submission.style.display = "block";
				});
			}
		};
	})
}

var search_button = document.querySelector("#search-button");
search_button.onclick = function () {
	var search_bar = document.querySelector("#search");
	var search = search_bar.value;
	fetch("http://localhost:8080/locations/" + search, {
		method: "GET",
		credentials: "include"
	}).then(function (response) {
		console.log(response.status);
		response.json().then(function (data) {
			locations = [data];
			console.log(locations)
			generateMarkers();
		});
	});
}

var main = function () {
	checkAuthentication();
};

main();
mymap.on('click', onMapClick);

/*
DATABASE - EXAMPLE CODE

CREATE TABLE locations (
    id INTEGER PRIMARY KEY,
    title TEXT,
    latitude FLOAT,
    longitude FLOAT,
    description TEXT,
    category TEXT);

INSERT INTO locations (title,description,latitude,longitude,category) VALUES ("The Habit","Burgers",4,10,"restuarant");
SELECT * FROM locations;
SELECT title, longitude FROM locations;
DELETE FROM locations;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    firstname TEXT,
    lastname TEXT,
    email TEXT,
    password TEXT);
*/

/*
CREATE DATABASE INSTRUCTIONS

sqlite3 mydb.db
*/