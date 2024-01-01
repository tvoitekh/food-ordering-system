CREATE TABLE Customer (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(15),
    UNIQUE (email)
);

ALTER TABLE customer
ADD COLUMN password_hash VARCHAR(255) NOT NULL;

CREATE TABLE Restaurant (
    restaurant_id INT PRIMARY KEY,
    restaurant_name VARCHAR(255) NOT NULL,
    reviews INT,
    rating FLOAT,
    price_range VARCHAR(10),
    UNIQUE (restaurant_name)
);


CREATE TABLE Cuisine (
    cuisine_id INT PRIMARY KEY,
    cuisine_name VARCHAR(255) NOT NULL,
    UNIQUE (cuisine_name)
);


CREATE TABLE Dishes (
    dish_id INT PRIMARY KEY,
    dish_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2),
    cuisine_id INT,
    FOREIGN KEY (cuisine_id) REFERENCES Cuisine(cuisine_id)
);

CREATE TABLE RestaurantCuisine (
    restaurant_id INT,
    cuisine_id INT,
    PRIMARY KEY (restaurant_id, cuisine_id),
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant(restaurant_id),
    FOREIGN KEY (cuisine_id) REFERENCES Cuisine(cuisine_id)
);


CREATE TABLE RestaurantDish (
    restaurant_id INTEGER REFERENCES Restaurant(restaurant_id),
    dish_id INTEGER REFERENCES Dishes(dish_id),
    PRIMARY KEY (restaurant_id, dish_id)
);



CREATE SEQUENCE customer_id_sequence START 1 OWNED BY food_ordering_system.customer.customer_id;

ALTER TABLE food_ordering_system.customer
ALTER COLUMN customer_id SET DEFAULT nextval('customer_id_sequence');
