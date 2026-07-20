PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

DELETE FROM mission_waypoints;
DELETE FROM missions;
DELETE FROM sqlite_sequence WHERE name IN ('missions', 'mission_waypoints');

INSERT INTO missions (id, name) VALUES
    (1, 'Mumbai Coastal Survey'),
    (2, 'Powai Lake Inspection'),
    (3, 'Airport Perimeter Training');

INSERT INTO mission_waypoints (
    mission_id,
    sequence,
    latitude,
    longitude,
    altitude_meters,
    speed_meters_per_second
) VALUES
    (1, 1, 18.9440, 72.8232, 60, 7),
    (1, 2, 18.9492, 72.8207, 70, 8),
    (1, 3, 18.9551, 72.8193, 70, 8),
    (1, 4, 18.9600, 72.8218, 60, 7),
    (2, 1, 19.1241, 72.9047, 55, 6),
    (2, 2, 19.1290, 72.9100, 65, 7),
    (2, 3, 19.1340, 72.9061, 65, 7),
    (2, 4, 19.1302, 72.8998, 55, 6),
    (3, 1, 19.1018, 72.8628, 75, 8),
    (3, 2, 19.1070, 72.8705, 85, 9),
    (3, 3, 19.1130, 72.8660, 85, 9),
    (3, 4, 19.1080, 72.8578, 75, 8);

COMMIT;
