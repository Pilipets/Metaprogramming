package uber.trip_manager_service.services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import uber.trip_manager_service.clients.DbClient;
import uber.trip_manager_service.clients.ProxyClient;
import uber.trip_manager_service.clients.SupplyLocationClient;
import uber.trip_manager_service.structures.external.SupplyInstance;
import uber.trip_manager_service.structures.internal.FilterTripParams;
import uber.trip_manager_service.structures.internal.TripForDB;
import uber.trip_manager_service.structures.internal.TripForDriver;
import uber.trip_manager_service.structures.internal.TripRequestEntity;
import uber.trip_manager_service.utils.ServiceNames;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service

public class BeforeTripService {
   private final SupplyLocationClient supplyLocationClient;
   private final DbClient dbClient;
   private final ProxyClient proxyClient;
   private final Trips__StorageDriver tripsStorage;

   private ResponseEntity<Object> resp = null;

   @Autowired
   BeforeTripService(
         final SupplyLocationClient supplyLocationClient,
         final DbClient dbClient,
         final ProxyClient proxyClient,
         final Trips__StorageDriver tripsStorage) {
      this.supplyLocationClient = supplyLocationClient;
      this.dbClient = dbClient;
      this.proxyClient = proxyClient;
      this.tripsStorage = tripsStorage;*/
   }

   private <T> boolean requestFailed(ResponseEntity<T> resp) {
      return resp.getStatusCode() != HttpStatus.OK || resp.getBody() == null;
   }

   public ResponseEntity<Object> newTripRequest(TripRequestEntity tripRequestEntity) {
      // get closest supply to given pick-up location
      var resp1 = supplyLocationClient.getClosestSupply(tripRequestEntity.getFrom());
      if (requestFailed(resp1)) {
         return new ResponseEntity(resp1.getBody(), resp1.getStatusCode());
      }

      List<SupplyInstance> closestSupply = resp1.getBody();

      // obtain ids from given supply
      List<UUID> filteredSupply = new ArrayList<>(closestSupply.size());
      for (SupplyInstance ins : closestSupply) {
         filteredSupply.add(ins.getId());
      }

      // perform call to the DB service to filter the points by given criteria
      FilterTripParams params = new FilterTripParams(tripRequestEntity.getParams());
      var resp2 = dbClient.filterSupply(params, filteredSupply);
      if (requestFailed(resp2)) {
         return new ResponseEntity(resp2.getStatusCode());
      }
      filteredSupply = resp2.getBody();

      // store hanging trip in the DB
      UUID tripId = tripsStorage.addPendingTrip(
            tripRequestEntity.getClientId(),
            tripRequestEntity.getFrom(),
            tripRequestEntity.getTo());

      // send the message to the DriverService through proxy, update the proxy with requestState
      Map<String, Object> driversTripPush = Map.of("trip_id", tripId, "driver_ids", filteredSupply);

      return proxyClient.sendDriversTripPush(
            ServiceNames.Drivers.getLabel(), driversTripPush);
   }

   public ResponseEntity<TripForDriver> acceptTrip(UUID driverId, UUID tripId) {
      TripForDB trip = tripsStorage.getRemovePending(tripId);
      if (trip == null) {
         return new ResponseEntity<>(HttpStatus.NO_CONTENT);
      }

      trip.setDriverId(driverId);
      trip.setStatus(TripForDB.TripStatus.ACCEPTED);

      // notify client about the trip accepted by Driver
      resp = proxyClient.tripAccepted(
            ServiceNames.Clients.getLabel(),
            trip.getClientId(),
            Map.of("tripId", trip.getTripId(), "driverId", driverId));

      if (requestFailed(resp)) {
         return new ResponseEntity<>(resp.getStatusCode());
      }

      // save trip as ongoing
      tripsStorage.addOngoingTrip(trip);

      // send trip to the Driver
      TripForDriver respTrip = new TripForDriver(driverId, tripId, trip.getFromLocation());
      return new ResponseEntity<>(respTrip, HttpStatus.OK);
   }
}
