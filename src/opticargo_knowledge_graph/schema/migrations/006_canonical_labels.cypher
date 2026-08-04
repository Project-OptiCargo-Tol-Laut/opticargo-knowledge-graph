// Add stable-ID constraints for canonical labels introduced after the operational core.
CREATE CONSTRAINT opticargo_user_id IF NOT EXISTS
FOR (n:User) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT opticargo_route_id IF NOT EXISTS
FOR (n:Route) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT opticargo_capacity_id IF NOT EXISTS
FOR (n:CargoCapacity) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT opticargo_listing_id IF NOT EXISTS
FOR (n:CargoListing) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT opticargo_recommendation_id IF NOT EXISTS
FOR (n:Recommendation) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT opticargo_booking_id IF NOT EXISTS
FOR (n:Booking) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT opticargo_payment_id IF NOT EXISTS
FOR (n:Payment) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT opticargo_document_id IF NOT EXISTS
FOR (n:Document) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT opticargo_review_id IF NOT EXISTS
FOR (n:Review) REQUIRE n.id IS UNIQUE;

CREATE INDEX opticargo_listing_status IF NOT EXISTS
FOR (n:CargoListing) ON (n.status);

CREATE INDEX opticargo_booking_status IF NOT EXISTS
FOR (n:Booking) ON (n.status);

CREATE INDEX opticargo_payment_status IF NOT EXISTS
FOR (n:Payment) ON (n.status);
