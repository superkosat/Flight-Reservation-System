# Flight Reservation System

![Home Page](homepage.png)

## Overview ##
Flight reservation system full stack web application built with flask and mysql. Front end bult with bootstrap, jquery for sorting and displaying data according to user-specified parameters and handle asynchronous requests.

## User types ##
Supports account creation of the following three user types via forms 
- Customer: can purchase flights on any airline subject to implicit regulations (i.e. flight has reached capacity)
- Airline Staff: can view ticket sales statistics for their airline, add booking agent affiliations, etc.
  - `operator` permission: allows staff user to modify flight statuses
  - `admin` permission: allows staff user to modify flights, airports, staff airline affiliations
- Booking Agent: once affiliated with an airline, can purchase flights on behalf of a customer and earn fixed rate commissions

## User Authentication ##
Sensitive user information, namely passwords, are salted and hashed from UTF-8 using SHA-256 encryption before they are stored in the database.

## Database Queries ##
All queries are sanitized prior to opening database cursor to prevent SQL injections


## Flights View ##
