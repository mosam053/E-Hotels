/* SQL View 1 creation code */
drop view if exists VW_AvailableRoomsPerArea;

CREATE VIEW VW_AvailableRoomsPerArea AS
SELECT H.city AS City, HC.chainName AS `Hotel Chain`, H.locationName AS Hotel, R.roomID AS `Room ID`, R.status AS `Room Availability`
FROM Hotels H
JOIN HotelChain HC ON H.chainName = HC.chainName
JOIN Rooms R ON H.hotelID = R.hotelID
WHERE R.status IS NULL;


/* SQL View 2 creation code */
drop view if exists VW_RoomCapacity;

CREATE VIEW VW_RoomCapacity AS 
SELECT 
    Hotels.locationName, 
    Rooms.roomID,
    Rooms.roomCapacity
FROM Hotels 
JOIN Rooms ON Hotels.hotelID = Rooms.hotelID;