CREATE TABLE HotelChain(
	chainName varchar(50),
	numHotels int,
	email varchar(50),
	phoneNumber varchar(15),
	PRIMARY KEY(chainName)
);

CREATE TABLE Hotels(
	locationName varchar(50),
	hotelID int,
	starRating int,
	numRooms int,
	street varchar(50),
	city varchar(50),
	province varchar(20),
	zip varchar(10),
	email varchar(50),
	phoneNumber varchar(15),
	managerSSN int,
	chainName varchar(50),
	PRIMARY KEY(hotelID),
	FOREIGN KEY (chainName) REFERENCES HotelChain(chainName)
);

CREATE TABLE Customer(
	SSN int,
	first_name varchar(50),
	last_name varchar(50),
	street varchar(50),
	city varchar(50),
	province varchar(20),
	zip varchar(10),
	username varchar(50),
	password varchar(50),
	PRIMARY KEY(SSN)
);


CREATE TABLE Employee(
	SSN int,
	first_name varchar(50),
	last_name varchar(50),
	street varchar(50),
	city varchar(50),
	province varchar(20),
	zip varchar(10),
	positions varchar(50),
	username varchar(50),
	password varchar(50),
	hotelID int,
	PRIMARY KEY(SSN),
	FOREIGN KEY (hotelID) REFERENCES Hotels(hotelID)
);

CREATE TABLE Rooms(
	roomID int,
	hotelID int,
	price int, 
	starRating int,
	hasWifi int,
	hasCoffeMaker int,
	hasJaccuzi int,
	viewType varchar(50),
	status varchar(50),
	extendable int,
	roomCapacity int,
	problems varchar(150),
	PRIMARY KEY(roomID),
	FOREIGN KEY (hotelID) REFERENCES Hotels(hotelID)
);


CREATE TABLE Bookings(
	bookingID int,
	bookingDate DATE,
	roomID int,
	SSN int,
	PRIMARY KEY (bookingID),
	FOREIGN KEY (roomID) REFERENCES Rooms(roomID),
	FOREIGN KEY (SSN) REFERENCES Customer(SSN)
);