package uber.trip_manager_service.services;

import org.springframework.stereotype.Service;
import uber.trip_manager_service.structures.internal.TripForDB;
import uber.trip_manager_service.structures.external.GeoPoint;

import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class TripsStorageDriver {
    private ConcurrentHashMap<UUID, TripForDB> cacheMap;

    // Normally here will be DB
private ConcurrentHashMap<UUID, TripForDB> ongoingMap;

    public UUID addPendingTrip(UUID clientId, GeoPoint where, GeoPoint to) {
        TripForDB trip = new TripForDB(clientId, where, to);
        cacheMap.put(trip.getTripId(), trip);
        return trip.getTripId();
    }

    public void addOngoingTrip(TripForDB trip) {
        trip.setStarted();

        ongoingMap.put(trip.getTripId(), trip);
    }
    public TripForDB getRemovePending(UUID tripId) {
        return cacheMap.remove(tripId);
    }

    public TripForDB getRemoveOngoing(UUID tripId) {
        return ongoingMap.remove(tripId);
    }

    public TripForDB getTrip(UUID tripId) {
        return cacheMap.getOrDefault(tripId, null);
    }
}