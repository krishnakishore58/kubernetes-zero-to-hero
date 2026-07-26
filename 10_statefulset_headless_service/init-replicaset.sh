#!/bin/bash
# Run this ONCE after all 3 pods are Running+Ready
# Initializes the MongoDB replica set using stable pod DNS names

kubectl exec -it mongo-0 -- mongosh --eval '
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-0.mongo.default.svc.cluster.local:27017" },
    { _id: 1, host: "mongo-1.mongo.default.svc.cluster.local:27017" },
    { _id: 2, host: "mongo-2.mongo.default.svc.cluster.local:27017" }
  ]
})'
