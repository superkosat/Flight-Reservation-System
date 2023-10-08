-- Alec Sirkin
-- CSCI-SHU 213 Databases
-- Course project part 1: table creation

CREATE TABLE `airline` (
  `name` varchar(64),
  PRIMARY KEY(`name`)
);


CREATE TABLE `airline_staff` (
  `username` varchar(64),
  `airline_name` varchar(64),
  `password` varchar(64),
  `first_name` varchar(64),
  `last_name` varchar(64),
  `dob` date,
  PRIMARY KEY(`username`),
  FOREIGN KEY(`airline_name`) REFERENCES `airline`(`name`)
);


CREATE TABLE `airplane` (
`airline_name` varchar(64),
`airplane_id` int(16),
`seats` int(11),
PRIMARY KEY(`airline_name`, `airplane_id`),
FOREIGN KEY(`airline_name`) REFERENCES `airline`(`name`)
);


CREATE TABLE `airport` (
`name` varchar(64),
`city` varchar(64),
PRIMARY KEY(`name`)
);


CREATE TABLE `booking_agent` (
`email` varchar(64),
`password` varchar(64),
`booking_agent_id` int(16),
`airline_name` varchar(64),
PRIMARY KEY(`email`),
FOREIGN KEY(`airline_name`) REFERENCES `airline`(`name`)
);


CREATE TABLE `customer` (
`email` varchar(64),
`name` varchar(64),
`password` varchar(64),
`building_num` varchar(64),
`street` varchar(64),
`city` varchar(64),
`state` varchar(64),
`phone_num` int(11),
`passport_num` varchar(64),
`passport_exp` date,
`passport_cty` varchar(64),
`dob` date,
PRIMARY KEY(`email`)
);


CREATE TABLE `flight` (
`airline_name` varchar(64),
`flight_num` int(11),
`airplane_id` int(11),
`dep_airport` varchar(64),
`arr_airport` varchar(64),
`status` varchar(64),
PRIMARY KEY(`airline_name`, `flight_num`),
FOREIGN KEY(`airline_name`) REFERENCES `airline`(`name`),
FOREIGN KEY(`dep_airport`) REFERENCES `airport`(`name`),
FOREIGN KEY(`arr_airport`) REFERENCES `airport`(`name`)
);


CREATE TABLE `ticket` (
`ticket_id` int(11),
`airline_name` varchar(64),
`flight_num` int(11),
PRIMARY KEY(`ticket_id`),
FOREIGN KEY(`airline_name`, `flight_num`) REFERENCES `flight`(`airline_name`, `flight_num`)
);


CREATE TABLE `purchases` (
`ticket_id` int(11),
`customer_email` varchar(64),
`booking_agent_id` int(11),
`purchase_date` date,
PRIMARY KEY(`ticket_id`, `customer_email`),
FOREIGN KEY(`ticket_id`) REFERENCES `ticket`(`ticket_id`),
FOREIGN KEY(`customer_email`) REFERENCES `customer`(`email`)
);