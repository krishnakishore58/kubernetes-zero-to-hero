# MongoDB Replica Set — StatefulSet + Headless Service Demo

## Files

| File | Description |
|------|-------------|
| `headless-svc.yaml` | Headless Service (`clusterIP: None`) |
| `statefulset.yaml` | MongoDB 3-node StatefulSet |
| `init-replicaset.sh` | One-time replica set init script |

---

## Step 1 — Deploy

```bash
kubectl apply -f headless-svc.yaml
kubectl apply -f statefulset.yaml
```

---

## Step 2 — Watch pods come up IN ORDER (0 → 1 → 2)

```bash
kubectl get pods -w -l app=mongo
```

> `mongo-0` starts first and must be `Ready` before `mongo-1` starts, then `mongo-2`.

---

## Step 3 — Verify each pod has its own PVC

```bash
kubectl get pvc
```

Expected output:
```
mongo-data-mongo-0   Bound
mongo-data-mongo-1   Bound
mongo-data-mongo-2   Bound
```

---

## Step 4 — Verify Headless DNS (no CLUSTER-IP)

```bash
kubectl get svc mongo
```

Expected output:
```
NAME    TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)
mongo   ClusterIP   None         <none>        27017/TCP
```

---

## Step 5 — Initialize the replica set

```bash
chmod +x init-replicaset.sh
./init-replicaset.sh
```

---

## Step 6 — Check PRIMARY / SECONDARY roles

```bash
kubectl exec -it mongo-0 -- mongosh --eval "rs.status()"
```

> Shows: `mongo-0` = PRIMARY, `mongo-1` = SECONDARY, `mongo-2` = SECONDARY

---

## Step 7 — Prove DNS resolves to direct pod IP (not a VIP)

```bash
kubectl run tmp --image=busybox --rm -it --restart=Never -- \
  nslookup mongo-0.mongo.default.svc.cluster.local
```

> Returns the direct pod IP — **not** a virtual IP. This is the Headless Service in action.

---

## Step 8 — Write on PRIMARY, read from SECONDARY

**Write on primary (`mongo-0`):**

```bash
kubectl exec -it mongo-0 -- mongosh --eval '
  db.getSiblingDB("demo").users.insertOne({ name: "kks", role: "admin" });
  db.getSiblingDB("demo").users.find().forEach(printjson);
'
```

**Read from secondary (`mongo-1`) — data replicated automatically**

```bash
kubectl exec -it mongo-1 -- mongosh --eval '
  db.getMongo().setReadPref("secondaryPreferred");
  db.getSiblingDB("demo").users.find().forEach(printjson);
'
```

---

## Step 9 — Prove self-healing with same identity

```bash
kubectl delete pod mongo-1
kubectl get pods -w
```

> `mongo-1` comes back with the **same name** and reattaches to `mongo-data-mongo-1` PVC — data is **not** lost.

---

## Step 10 — Cleanup

```bash
kubectl delete -f statefulset.yaml
kubectl delete -f headless-svc.yaml
kubectl delete pvc -l app=mongo
```

> ⚠️ PVCs are **not** auto-deleted when a StatefulSet is removed — you must delete them manually.

---

## Why Headless + StatefulSet together?

| Component | What it provides |
|-----------|-----------------|
| StatefulSet | Stable pod names: `mongo-0`, `mongo-1`, `mongo-2` |
| Headless Service | Stable DNS per pod: `mongo-0.mongo.default.svc.cluster.local` |
| `volumeClaimTemplates` | Each pod gets its own PVC, permanently bound by name |
| Together | Replica set members discover each other; clients can target PRIMARY vs SECONDARY directly — impossible with a regular Deployment + Service |

