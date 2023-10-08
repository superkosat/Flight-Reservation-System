-- Alec Sirkin
-- CSCI-SHU 213 Databases
-- Course project part 2: inserts


INSERT INTO `airline` (`name`) VALUES
('China Eastern'),
('American'),
('Cathay Pacific'),
('Emirates');


INSERT INTO `airport` (`name`, `city`) VALUES
('JFK', 'New York'),
('PVG', 'Shanghai'),
('DXB', 'Dubai'),
('YVR', 'Vancouver'),
('HKG', 'Hong Kong');


INSERT INTO `customer` (`email`, `name`, `password`, `building_num`, `street`, `city`, `state`, `phone_num`, `passport_num`, `passport_exp`, `passport_cty`, `dob`) VALUES
('asdas@example.com', 'Jane Doe', 'da3r4r33', '1000', 'Boston Post Rd.', 'Rye', 'New York', 9140081, '988722355', '2025-02-02', 'United States', '2000-05-06'),
('1234@nyu.edu', 'Stone McDermott', 'Swu2y39Y#', '24', 'Castle Hill Dr.', 'Greenwich', 'Connecticut', 2031109, '465729082', '2030-11-30', 'United States', '2001-08-25');


INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`, `airline_name`) VALUES
('smi13je@gmail.com', '8di23%26iss', 101248, 'China Eastern');


INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seats`) VALUES
('American', 12344, 205),
('Emirates', 22907, 380),
('Cathay Pacific', 229761, 220),
('China Eastern', 88721, 205);


INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `dob`, `airline_name`) VALUES
('jdoe420', '1O@UE*YD*&^*DS', 'John', 'Doe', '1990-01-01', 'American'),
('maziz009', 'adoid8w3oeio3e', 'Mohammed', 'Aziz', '1965-04-03', 'Emirates'),
('lzhang', 'ndjb23bk23r2oihOI@#', 'Li', 'Zhang', '1999-07-16', 'China Eastern');


INSERT INTO `flight` (`airline_name`, `flight_num` , `airplane_id`, `dep_airport`, `arr_airport`, `status`) VALUES
('American', 2908, 12344, 'YVR', 'JFK', 'delayed'),
('Cathay Pacific', 992, 229761, 'HKG', 'JFK', 'in progress'),
('Cathay Pacific', 301, 229761, 'JFK', 'PVG', 'upcoming'),
('China Eastern', 639, 88721, 'PVG', 'DXB', 'upcoming'),
('Emirates', 3200, 22907, 'DXB', 'JFK', 'delayed');


INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
(1, 'Cathay Pacific', 992),
(2, 'Cathay Pacific', 301),
(3, 'China Eastern', 639),
(4, 'American', 2908),
(5, 'American', 2908),
(6, 'Emirates', 3200);

INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
(1, 'asdas@example.com', NULL, '2023-10-02'),
(6, '1234@nyu.edu', 101248, '2023-09-10');


